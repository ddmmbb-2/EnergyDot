import cupy as cp

class EnergyLatticeSim3D:
    def __init__(self, size=96, mode="micro"):
        self.S = size
        self.mid = size // 2
        
        # --- 🔴 核心升級 1：導入時間維度，支撐波動力學與慣性 ---
        # u 代表當前狀態 t，u_prev 代表上一時刻 t-1
        self.u = cp.zeros((3, size, size, size), dtype=cp.float32)
        self.u_prev = cp.zeros((3, size, size, size), dtype=cp.float32)
        
        # 波速的平方 (相當於 c^2，決定波的傳播與彈性介質的剛性)
        self.alpha = 0.08
        self.set_mode(mode)

    def set_mode(self, mode):
        if mode == "micro":
            self.void_R = 2.0 * (self.S / 96.0)
            self.displacement_mag = -0.5 * (self.S / 96.0)

    def inject_particle(self, pos, mass, charge, spin_vector, radius=5.0):
        """
        --- 🔴 核心升級 2：大一統通用粒子注入器 ---
        將粒子的內稟屬性完全對應到空間晶格的幾何形變
        """
        z, y, x = cp.ogrid[:self.S, :self.S, :self.S]
        dz, dy, dx = z - pos[0], y - pos[1], x - pos[2]
        
        # 計算距離並避免除以零
        dist = cp.sqrt(dx**2 + dy**2 + dz**2)
        dist_safe = cp.maximum(dist, 1e-5) 
        
        # 建立 4D 遮罩以符合 (3, S, S, S) 的形狀疊加
        mask_4d = (dist <= radius)[cp.newaxis, :, :, :]
        
        # 1. 徑向單位向量 (基底)
        dir_x = dx / dist_safe
        dir_y = dy / dist_safe
        dir_z = dz / dist_safe
        radial_field = cp.stack([dir_x, dir_y, dir_z], axis=0)
        
        # 2. 電荷場：純粹的散度源 (向外推擠或向內拉扯)
        charge_field = charge * radial_field * (1.0 / dist_safe)
        
        # 3. 質量場：等向性排擠空間
        mass_field = mass * radial_field * (1.0 / dist_safe)
        
        # 4. 自旋場：渦旋向量，產生旋度 (切向剪切應力)
        sx, sy, sz = spin_vector
        # 🛠️ 修正點：提早除以 dist_safe，強制觸發廣播展開為 (S, S, S)
        vtx_x = (sy * dz - sz * dy) / dist_safe
        vtx_y = (sz * dx - sx * dz) / dist_safe
        vtx_z = (sx * dy - sy * dx) / dist_safe
        spin_field = cp.stack([vtx_x, vtx_y, vtx_z], axis=0)
        
        # --- 物理量疊加 ---
        perturbation = (mass_field + charge_field + spin_field) * mask_4d
        
        # 同時注入當前與前一狀態，確保粒子初始為「靜止」不具相速度
        self.u += perturbation
        self.u_prev += perturbation
        
        print(f"⚛️ 粒子注入完成 | 位置: {pos} | 質量: {mass} | 電荷: {charge:.2f} | 自旋: {spin_vector}")

    def inject_real_electron(self, pos, sign=1.0, spin=0.0):
        """
        --- 向下相容 Wrapper ---
        為了讓舊版 GUI 可以直接呼叫，不需修改 GUI 程式碼
        """
        alpha_e = 1.0 / 137.036
        base_density = 20.0 * (1.0 + alpha_e) * sign
        
        # 將電子的特徵轉換為通用粒子的參數
        mass = 0.511              # 質量特徵
        charge = base_density     # 電荷強度與正負
        spin_vector = (0, 0, spin) # 預設繞 Z 軸自旋
        
        self.inject_particle(pos, mass, charge, spin_vector, radius=5.0)

    def step(self):
        """
        --- 🔴 核心升級 3：真正的波動力學 ---
        使用離散波動方程式： u(t+1) = 2u(t) - u(t-1) + c^2 ∇² u
        讓粒子交互作用具備「慣性」與「波動傳遞」特性
        """
        u_next = cp.zeros_like(self.u)
        
        for i in range(3):
            u_comp = self.u[i]
            laplacian = (
                cp.roll(u_comp, 1, axis=0) + cp.roll(u_comp, -1, axis=0) +
                cp.roll(u_comp, 1, axis=1) + cp.roll(u_comp, -1, axis=1) +
                cp.roll(u_comp, 1, axis=2) + cp.roll(u_comp, -1, axis=2) - 6 * u_comp
            )
            
            # 波動方程式演化
            u_next[i] = 2.0 * u_comp - self.u_prev[i] + self.alpha * laplacian
            
        # 更新時間步 (時間往前推移)
        self.u_prev = self.u.copy()
        self.u = u_next