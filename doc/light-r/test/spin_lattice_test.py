import cupy as cp
import numpy as np
import matplotlib.pyplot as plt

class MicropolarLatticeSim:
    def __init__(self, size=100):
        self.S = size
        self.mid = size // 2
        
        # 1. 傳統的平移位移場 (推擠) [x, y, z]
        self.u = cp.zeros((3, size, size, size), dtype=cp.float32)
        self.u_old = cp.zeros_like(self.u)
        
        # 2. 全新的旋轉場 (原地扭轉角度) [theta_x, theta_y, theta_z]
        self.theta = cp.zeros((3, size, size, size), dtype=cp.float32)
        self.theta_old = cp.zeros_like(self.theta)
        
        # 彈性參數
        self.alpha = 0.1  # 推擠傳遞速度 (重力波/縱波極限)
        self.gamma = 0.1  # 扭轉傳遞速度
        self.kappa = 0.05 # 耦合係數 (推擠與扭轉互相轉換的齒輪咬合力)

    def get_laplacian(self, field):
        """計算拉普拉斯算子 (擴散趨勢)"""
        f_up    = cp.roll(field,  1, axis=1)
        f_down  = cp.roll(field, -1, axis=1)
        f_left  = cp.roll(field,  1, axis=2)
        f_right = cp.roll(field, -1, axis=2)
        f_front = cp.roll(field,  1, axis=0)
        f_back  = cp.roll(field, -1, axis=0)
        return f_up + f_down + f_left + f_right + f_front + f_back - 6 * field

    def get_curl(self, field):
        """計算旋度 (向量場的渦旋趨勢)"""
        # 這裡 field[0]=z分量, field[1]=y分量, field[2]=x分量 (依據形狀習慣)
        # 為簡化，我們實作標準中心差分旋度 (∇ × F)
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

    def step(self):
        # 取得兩個場的 Laplacians
        lap_u = self.get_laplacian(self.u)
        lap_theta = self.get_laplacian(self.theta)
        
        # 取得兩個場的 Curls (互相咬合的關鍵)
        curl_u = self.get_curl(self.u)
        curl_theta = self.get_curl(self.theta)
        
        # --- 微極彈性波動方程式 (Cosserat Equations) ---
        # 位移場更新：除了推擠擴散，還會被扭轉場的旋度牽引
        u_next = 2 * self.u - self.u_old + self.alpha * lap_u + self.kappa * curl_theta
        
        # 旋轉場更新：除了扭轉擴散，還會被位移場的旋度牽引，並有恢復力距 (-2*kappa*theta)
        theta_next = 2 * self.theta - self.theta_old + self.gamma * lap_theta + self.kappa * curl_u - 2 * self.kappa * self.theta
        
        # 更新時間步
        self.u_old = self.u.copy()
        self.theta_old = self.theta.copy()
        self.u = u_next
        self.theta = theta_next

def run_spin_experiment():
    print("🌀 啟動微極彈性測試：旋轉自由度與橫波湧現")
    sim = MicropolarLatticeSim(size=80)
    
    # 在中心注入一個「純粹的扭轉 (Spin)」，不給予任何推擠位移
    # 讓中心的巴克球沿著 Z 軸強烈旋轉
    sim.theta[0, sim.mid, sim.mid, sim.mid] = 5.0 
    
    distances = np.array([10, 20, 30], dtype=int)
    sensor_history_u = {d: [] for d in distances}
    sensor_history_theta = {d: [] for d in distances}
    
    print("演化中...")
    total_steps = 150
    for t in range(total_steps):
        sim.step()
        # 觀察位移場 (u) 是否因為旋轉而被「無中生有」地激發出來！
        for d in distances:
            u_mag = float(cp.linalg.norm(sim.u[:, sim.mid, sim.mid, sim.mid + d]))
            sensor_history_u[d].append(u_mag)
            
    # 繪圖
    plt.figure(figsize=(8,5))
    for d in distances:
        plt.plot(sensor_history_u[d], label=f'Distance {d} (Displacement u)')
        
    plt.xlabel('Time Steps')
    plt.ylabel('Induced Displacement Magnitude |u|')
    plt.title('Emergence of Transverse Wave from Pure Spin')
    plt.legend()
    plt.grid(True)
    plt.savefig('spin_transverse_wave.png')
    print("🖼️ 圖表已儲存至: spin_transverse_wave.png")
    plt.show()

if __name__ == "__main__":
    run_spin_experiment()