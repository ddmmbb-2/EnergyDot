import cupy as cp
import numpy as np

class EnergyLatticeSim3D_Relativity:
    def __init__(self, size=96, alpha=0.08):
        self.S = size
        self.alpha = alpha
        self.mid = self.S // 2
        
        # 🔴 升級 1：從純量升級為向量
        # 位移向量場 u = (u_x, u_y, u_z)
        # 初始為 0，代表沒有物質時的「平直時空 (Minkowski Spacetime)」
        self.u = cp.zeros((3, self.S, self.S, self.S), dtype=cp.float32)
        
        # 空洞 (物質) 參數
        self.void_pos = (self.mid, self.mid, self.mid)
        self.void_R = 6.0

    def apply_void_boundary(self):
        """
        🔴 升級 2：應力-能量張量 T_uv 的幾何化
        物質空洞不再是「壓力變0」，而是強行將周圍晶格往內拉扯 (引力塌陷)
        """
        z, y, x = cp.ogrid[:self.S, :self.S, :self.S]
        dz = z - self.void_pos[0]
        dy = y - self.void_pos[1]
        dx = x - self.void_pos[2]
        
        dist = cp.sqrt(dx**2 + dy**2 + dz**2)
        dist = cp.maximum(dist, 1e-5) # 避免除以零
        
        # 在空洞半徑內，強行設定徑向位移
        mask = dist <= self.void_R
        
        # 負號代表向內塌陷 (時空向質量中心彎曲)
        displacement_mag = -3.0  
        
        # 將位移量分解到 x, y, z 三個維度 (這就是度規擾動的源頭)
        self.u[0][mask] = displacement_mag * (dx / dist)[mask]
        self.u[1][mask] = displacement_mag * (dy / dist)[mask]
        self.u[2][mask] = displacement_mag * (dz / dist)[mask]

    def step(self):
        """
        🔴 升級 3：愛因斯坦真空場方程的晶格等價演化
        因為 λ = -μ，納維彈性方程簡化為三個獨立的 ∇² u = 0
        """
        self.apply_void_boundary()
        
        # 對 x, y, z 三個位移分量獨立進行拉普拉斯演化
        for i in range(3):
            u_comp = self.u[i]
            u_up    = cp.roll(u_comp,  1, axis=1)
            u_down  = cp.roll(u_comp, -1, axis=1)
            u_left  = cp.roll(u_comp,  1, axis=2)
            u_right = cp.roll(u_comp, -1, axis=2)
            u_front = cp.roll(u_comp,  1, axis=0)
            u_back  = cp.roll(u_comp, -1, axis=0)
            
            laplacian = (u_up + u_down + u_left + u_right + u_front + u_back - 6 * u_comp)
            
            # 尋求靜態度規 (Static Metric) 解
            self.u[i] = u_comp + self.alpha * laplacian

    def get_metric_perturbation_2d(self):
        """
        🔴 升級 4：提取應變張量，等價於提取時空度規擾動 h_ij
        """
        # 擷取 Z = mid 的 2D 切片
        ux_slice = self.u[0, self.mid, :, :].get()
        uy_slice = self.u[1, self.mid, :, :].get()
        
        # 計算應變張量 (度規擾動) ε_ij = 0.5 * (∂_i u_j + ∂_j u_i)
        dux_dx = np.gradient(ux_slice, axis=1)
        duy_dy = np.gradient(uy_slice, axis=0)
        
        # 返回形變場，用於繪製「彎曲時空」
        return ux_slice, uy_slice, dux_dx, duy_dy