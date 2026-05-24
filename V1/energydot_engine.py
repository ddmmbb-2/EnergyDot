import cupy as cp

class EnergyLatticeSim3D:
    def __init__(self, size=96, mode="micro"):
        self.S = size
        self.mid = size // 2
        
        # 1. 空間平移位移場 (推擠 / 萬有引力與純量場)
        self.u = cp.zeros((3, size, size, size), dtype=cp.float32)
        self.u_prev = cp.zeros((3, size, size, size), dtype=cp.float32)
        
        # 2. 空間旋轉場 (自旋 / 電磁波與橫波)
        self.theta = cp.zeros((3, size, size, size), dtype=cp.float32)
        self.theta_prev = cp.zeros((3, size, size, size), dtype=cp.float32)
        
        # 宇宙彈性參數
        self.alpha = 0.08    # 推擠波速 (重力極限)
        self.gamma = 0.08    # 扭轉波速 (光速極限)
        self.kappa = 0.0001  # 齒輪咬合力 (推擠與自旋的耦合係數)
        self.beta = 0.05     # 晶格週期性勢能係數 (Sine-Gordon 非線性束縛強度)
        self.skyrme = 0.05   # 🌟 新增：Skyrme 剛性係數 (對抗 3D 空間坍縮的高階非線性彈性極限)
        
        self.set_mode(mode)
        
        # 靜態鎖定遮罩 (用於維持黑洞等拓撲缺陷)
        self.lock_mask = cp.zeros((1, size, size, size), dtype=bool)
        self.lock_field_u = cp.zeros((3, size, size, size), dtype=cp.float32)
        self.lock_field_theta = cp.zeros((3, size, size, size), dtype=cp.float32)

    def set_mode(self, mode):
        pass # 保留相容性介面

    def inject_black_hole(self, pos, mass, charge, radius=10.0, spin_vector=(0.0, 0.0, 0.0)):
        """🌌 黑洞生成器升級版：支援自旋鎖定"""
        z, y, x = cp.ogrid[:self.S, :self.S, :self.S]
        dz, dy, dx = z - pos[0], y - pos[1], x - pos[2]
        dist = cp.sqrt(dx**2 + dy**2 + dz**2)
        dist_safe = cp.maximum(dist, 1e-5) 
        
        mask_4d = (dist <= radius)[cp.newaxis, :, :, :]
        
        dir_x = dx / dist_safe
        dir_y = dy / dist_safe
        dir_z = dz / dist_safe
        radial_field = cp.stack([dir_x, dir_y, dir_z], axis=0)
        
        # 質量引發的極端推擠場
        mass_field = mass * radial_field * (1.0 / dist_safe)
        
        # 自旋引發的極端扭轉場
        spin_field = cp.stack([
            cp.full_like(dist, spin_vector[0]),
            cp.full_like(dist, spin_vector[1]),
            cp.full_like(dist, spin_vector[2])
        ], axis=0) * (1.0 / dist_safe)
        
        self.lock_mask = self.lock_mask | mask_4d
        self.lock_field_u += mass_field * mask_4d
        self.lock_field_theta += spin_field * mask_4d
        
        self.u = cp.where(self.lock_mask, self.lock_field_u, self.u)
        self.theta = cp.where(self.lock_mask, self.lock_field_theta, self.theta)
        
        self.u_prev = self.u.copy()
        self.theta_prev = self.theta.copy()
        
    def get_laplacian(self, field):
        """計算拉普拉斯算子 (修正張量軸向：對空間 axis 1, 2, 3 進行傳遞)"""
        f_z_up   = cp.roll(field, -1, axis=1)
        f_z_down = cp.roll(field,  1, axis=1)
        f_y_up   = cp.roll(field, -1, axis=2)
        f_y_down = cp.roll(field,  1, axis=2)
        f_x_up   = cp.roll(field, -1, axis=3)
        f_x_down = cp.roll(field,  1, axis=3)
        return f_z_up + f_z_down + f_y_up + f_y_down + f_x_up + f_x_down - 6 * field

    def get_curl(self, field):
        """計算旋度"""
        dy_fz = (cp.roll(field[0], -1, axis=1) - cp.roll(field[0], 1, axis=1)) / 2.0
        dz_fy = (cp.roll(field[1], -1, axis=0) - cp.roll(field[1], 1, axis=0)) / 2.0
        
        dz_fx = (cp.roll(field[2], -1, axis=0) - cp.roll(field[2], 1, axis=0)) / 2.0
        dx_fz = (cp.roll(field[0], -1, axis=2) - cp.roll(field[0], 1, axis=2)) / 2.0
        
        dx_fy = (cp.roll(field[1], -1, axis=2) - cp.roll(field[1], 1, axis=2)) / 2.0
        dy_fx = (cp.roll(field[2], -1, axis=1) - cp.roll(field[2], 1, axis=1)) / 2.0
        
        curl_x = dy_fz - dz_fy
        curl_y = dz_fx - dx_fz
        curl_z = dx_fy - dy_fx
        return cp.stack([curl_z, curl_y, curl_x], axis=0)

    def get_skyrme_stabilizer(self, field):
        """🌟 新增：計算 Skyrme 高階非線性彈性剛性力 (Divergence of non-linear gradient flux)
        數學公式：∇ · (||∇f||² ∇f) 
        當場的梯度極高時，此項會自發產生巨大的排斥力，阻止幾何結構收縮成奇點。
        """
        # 計算一階空間中央差分梯度 (軸 1=Z, 軸 2=Y, 軸 3=X)
        df_dz = (cp.roll(field, -1, axis=1) - cp.roll(field, 1, axis=1)) / 2.0
        df_dy = (cp.roll(field, -1, axis=2) - cp.roll(field, 1, axis=2)) / 2.0
        df_dx = (cp.roll(field, -1, axis=3) - cp.roll(field, 1, axis=3)) / 2.0
        
        # 計算梯度模長的平方 (各分量空間梯度的總和)
        grad_norm_sq = df_dx**2 + df_dy**2 + df_dz**2
        
        # 計算非線性通量 (Flux) = ||∇f||² * ∇f
        flux_z = grad_norm_sq * df_dz
        flux_y = grad_norm_sq * df_dy
        flux_x = grad_norm_sq * df_dx
        
        # 計算通量的散度 (Divergence)
        div_flux = ((cp.roll(flux_z, -1, axis=1) - cp.roll(flux_z, 1, axis=1)) / 2.0 +
                    (cp.roll(flux_y, -1, axis=2) - cp.roll(flux_y, 1, axis=2)) / 2.0 +
                    (cp.roll(flux_x, -1, axis=3) - cp.roll(flux_x, 1, axis=3)) / 2.0)
        return div_flux

    def step(self):
        """🔴 大一統波動演化：Cosserat 微極彈性力學 + Sine-Gordon 非線性項 + Skyrme 剛性項"""
        if not hasattr(self, 'damping_mask'):
            self.damping_mask = cp.ones((self.S, self.S, self.S), dtype=cp.float32)
            margin = 15
            z, y, x = cp.ogrid[:self.S, :self.S, :self.S]
            mask_edge = (x < margin) | (x >= self.S - margin) | \
                        (y < margin) | (y >= self.S - margin) | \
                        (z < margin) | (z >= self.S - margin)
            self.damping_mask[mask_edge] = 0.95

        # 1. 基礎色散與扭轉運算
        lap_u = self.get_laplacian(self.u)
        lap_theta = self.get_laplacian(self.theta)
        
        curl_u = self.get_curl(self.u)
        curl_theta = self.get_curl(self.theta)
        
        # 2. 晶格週期性勢能束縛 (Sine-Gordon 非線性)
        nonlinear_u = self.beta * cp.sin(self.u)
        nonlinear_theta = self.beta * cp.sin(self.theta)
        
        # 3. 🌟 Skyrme 高階非線性幾何剛性力
        skyrme_force_u = self.get_skyrme_stabilizer(self.u)
        skyrme_force_theta = self.get_skyrme_stabilizer(self.theta)
        
        # 4. 互相咬合的完整動力學演化方程式
        # Skyrme 項的符號與拉普拉斯算子一致，在形變極大處提供強大的幾何反向彈性阻力
        u_next = (2.0 * self.u - self.u_prev + 
                  self.alpha * lap_u + 
                  self.kappa * curl_theta - 
                  nonlinear_u + 
                  self.skyrme * skyrme_force_u)
                  
        theta_next = (2.0 * self.theta - self.theta_prev + 
                      self.gamma * lap_theta + 
                      self.kappa * curl_u - 
                      2.0 * self.kappa * self.theta - 
                      nonlinear_theta + 
                      self.skyrme * skyrme_force_theta)
        
        # 5. 靜態拓撲缺陷強制鎖定 (若有啟用黑洞等機制)
        if cp.any(self.lock_mask):
            u_next = cp.where(self.lock_mask, self.lock_field_u, u_next)
            theta_next = cp.where(self.lock_mask, self.lock_field_theta, theta_next)
            
        # 邊界阻尼吸收廢熱 (自動廣播至 4D 張量)
        u_next *= self.damping_mask
        theta_next *= self.damping_mask
        
        self.u_prev = self.u.copy()
        self.theta_prev = self.theta.copy()
        self.u = u_next
        self.theta = theta_next