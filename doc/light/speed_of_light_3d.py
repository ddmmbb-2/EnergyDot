import cupy as cp
import numpy as np
import matplotlib.pyplot as plt

class LightSpeedSim3DGPU:
    def __init__(self, size=120, alpha=0.1):
        # 使用 120x120x120 的大空間，確保波有足夠的距離奔跑
        self.S = size
        self.alpha = alpha  # 🔴 晶格彈性系數：這決定了光速的快慢
        
        # 初始化完美的靜態平衡背景 (壓力全部為 1.0)
        self.P = cp.ones((self.S, self.S, self.S), dtype=cp.float32)
        self.P_old = self.P.copy()
        
        # 宇宙正中心
        self.mid = self.S // 2

    def inject_pulse(self):
        """光子激發：在宇宙中心強行打入一個極短促的高壓脈衝 (光子誕生)"""
        self.P[self.mid, self.mid, self.mid] = 10.0

    def step(self):
        """3D 波動傳導"""
        P_up    = cp.roll(self.P,  1, axis=1)
        P_down  = cp.roll(self.P, -1, axis=1)
        P_left  = cp.roll(self.P,  1, axis=2)
        P_right = cp.roll(self.P, -1, axis=2)
        P_front = cp.roll(self.P,  1, axis=0)
        P_back  = cp.roll(self.P, -1, axis=0)
        
        laplacian = (P_up + P_down + P_left + P_right + P_front + P_back - 6 * self.P)
        
        # 純波動方程 (這次不加阻尼，讓光信號無損地傳播到遠方)
        P_next = 2 * self.P - self.P_old + self.alpha * laplacian
        
        self.P_old = self.P.copy()
        self.P = P_next

def run_light_speed_experiment():
    print("開始執行 EnergyDot 宇宙常數實驗：探測微觀光速 (c)...")
    
    sim = LightSpeedSim3DGPU(size=120, alpha=0.1)
    
    # 在第 0 步打入脈衝
    sim.inject_pulse()
    
    # 設定四個不同距離的「天文觀測站」，觀測點固定在 X 軸上
    sensor_distances = np.array([20, 30, 40, 50])
    arrival_times = []
    
    # 建立每個觀測站的數據記錄器
    sensor_history = {d: [] for d in sensor_distances}
    
    total_steps = 160
    print(f"正在讓光子在 GPU 晶格海中奔跑 {total_steps} 步...")
    
    for t in range(total_steps):
        sim.step()
        
        # 記錄各觀測站當前的壓力訊號
        for d in sensor_distances:
            # 讀取對應坐標上的球球壓力值
            p_val = float(sim.P[sim.mid, sim.mid, sim.mid + d])
            sensor_history[d].append(p_val)
            
    print("\n--- 觀測站數據分析（改用前緣偵測法） ---")  # 🔴 已修正為 print
    for d in sensor_distances:
        history = np.array(sensor_history[d])
        
        # 修正：不再抓最大值，而是抓第一個突破背景噪聲 (例如 > 1.001) 的步數
        arrival_indices = np.where(history > 1.001)[0]
        
        if len(arrival_indices) > 0:
            peak_time = int(arrival_indices[0])
        else:
            peak_time = total_steps
            
        arrival_times.append(peak_time)
        c_local = d / peak_time if peak_time > 0 else 0
        print(f"觀測站 距離 R = {d} 處：第一道光在第 {peak_time:3d} 步抵達 | 湧現光速 c = {c_local:.5f} 格/步")

    # --- 驗證光速是否為常數（線性擬合） ---
    arrival_times = np.array(arrival_times)
    slope, intercept = np.polyfit(arrival_times, sensor_distances, 1)
    print("---------------------------------------")
    print(f"🏆 終極驗證結果：這套時空結構的巨觀光速 c = {slope:.5f} (格/步)")
    print(f"公式自洽度 (R² 線性度): {np.corrcoef(arrival_times, sensor_distances)[0,1]**2:.6f} (越接近 1 代表光速越恆定)")
    
    # 繪製時空圖 (Spacetime Diagram)
    plt.figure(figsize=(7, 5))
    plt.plot(arrival_times, sensor_distances, 'ro-', lw=2, label='Measured Light Front')
    plt.plot(arrival_times, slope * arrival_times + intercept, 'k--', label=f'Perfect Linear Limit (c={slope:.3f})')
    plt.xlabel('Time (Simulation Steps)')
    plt.ylabel('Distance from Source (R)')
    plt.title('Spacetime Diagram: Emergent Speed of Light')
    plt.legend()
    plt.grid(True)
    plt.savefig('speed_of_light_success.png')
    plt.show()

if __name__ == "__main__":
    run_light_speed_experiment()