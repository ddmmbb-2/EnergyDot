import cupy as cp

class EnergyLatticeSim3DGPU:
    def __init__(self, size=96, alpha=0.08):  # 🔴 這裡改成 96
        self.S = size
        self.alpha = alpha  
        
        # 初始化 3D 壓力場
        self.P = cp.random.normal(1.0, 0.02, size=(self.S, self.S, self.S), dtype=cp.float32)
        self.P_old = self.P.copy()
        
        # 設定中心平面
        self.mid = self.S // 2
        self.cA_x = self.S // 3
        self.cB_x = (self.S * 2) // 3

    def apply_substance_defects(self):
        """3D 物質缺陷：在三維空間中創造兩個球形的收縮凹陷源"""
        z, y, x = cp.ogrid[:self.S, :self.S, :self.S]
        
        # 稍微放大缺陷半徑到 4.5，讓它在更大的空間中依然保持穩定的凹陷場
        mask_A = ((z - self.mid)**2 + (y - self.mid)**2 + (x - self.cA_x)**2) <= 4.5**2
        mask_B = ((z - self.mid)**2 + (y - self.mid)**2 + (x - self.cB_x)**2) <= 4.5**2
        
        self.P[mask_A] = 0.0
        self.P[mask_B] = 0.0

    def step(self):
        """3D 彈性晶格壓力傳導演算法"""
        self.apply_substance_defects()
        
        P_up    = cp.roll(self.P,  1, axis=1)
        P_down  = cp.roll(self.P, -1, axis=1)
        P_left  = cp.roll(self.P,  1, axis=2)
        P_right = cp.roll(self.P, -1, axis=2)
        P_front = cp.roll(self.P,  1, axis=0)
        P_back  = cp.roll(self.P, -1, axis=0)
        
        laplacian = (P_up + P_down + P_left + P_right + P_front + P_back - 6 * self.P)
        P_next = 2 * self.P - self.P_old + self.alpha * laplacian
        
        P_next = self.P + (P_next - self.P) * 0.95
        
        self.P_old = self.P.copy()
        self.P = P_next
        
    def measure_net_force_3d(self):
        """量測 3D 空間中的應力梯度淨合力"""
        # 🔴 隨著盒子變大，採樣立體切片的外延半徑也對應微調拉寬（cA_x - 8 到 -4）
        left_vol = cp.mean(self.P[self.mid-4:self.mid+4, self.mid-4:self.mid+4, self.cA_x-9:self.cA_x-4])
        right_vol = cp.mean(self.P[self.mid-4:self.mid+4, self.mid-4:self.mid+4, self.cA_x+4:self.cA_x+9])
        
        net_force_x = left_vol - right_vol
        return float(net_force_x)