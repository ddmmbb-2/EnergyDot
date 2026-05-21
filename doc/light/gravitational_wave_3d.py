import cupy as cp
import numpy as np
import matplotlib.pyplot as plt

class GravityWaveSim3DGPU:
    def __init__(self, size=120, alpha=0.1):
        self.S = size
        self.alpha = alpha
        
        # 初始化完美的靜態背景
        self.P = cp.ones((self.S, self.S, self.S), dtype=cp.float32)
        self.P_old = self.P.copy()
        
        self.mid = self.S // 2
        self.particle_exists = True

    def apply_particle_defect(self):
        """如果在前 50 步，粒子存在，強行維持重力凹陷凹陷"""
        if self.particle_exists:
            z, y, x = cp.ogrid[:self.S, :self.S, :self.S]
            mask = ((z - self.mid)**2 + (y - self.mid)**2 + (x - self.mid)**2) <= 4.5**2
            self.P[mask] = 0.0

    def step(self):
        """3D 晶格壓力傳導"""
        self.apply_particle_defect()
        
        P_up    = cp.roll(self.P,  1, axis=1)
        P_down  = cp.roll(self.P, -1, axis=1)
        P_left  = cp.roll(self.P,  1, axis=2)
        P_right = cp.roll(self.P, -1, axis=2)
        P_front = cp.roll(self.P,  1, axis=0)
        P_back  = cp.roll(self.P, -1, axis=0)
        
        laplacian = (P_up + P_down + P_left + P_right + P_front + P_back - 6 * self.P)
        
        # 純波動方程
        P_next = 2 * self.P - self.P_old + self.alpha * laplacian
        
        self.P_old = self.P.copy()
        self.P = P_next

def run_gravity_wave_experiment():
    print("開始執行 EnergyDot 宇宙常數實驗：探測動態重力波速 (v_g)...")
    
    sim = GravityWaveSim3DGPU(size=120, alpha=0.1)
    
    # 觀測站設定在距離中心 R = 20, 30, 40, 50 處
    sensor_distances = np.array([20, 30, 40, 50])
    arrival_times = []
    sensor_history = {d: [] for d in sensor_distances}
    
    # 前 50 步：建立穩定的靜態重力場
    print("正在建立穩定的靜態重力場（時空彎曲中）...")
    for t in range(50):
        sim.step()
        
    # 第 50 步：粒子湮滅！重力波爆發！
    print("💥 第 50 步：基本粒子突然湮滅！重力波漣漪爆發！")
    sim.particle_exists = False
    
    # 繼續模擬 160 步，觀察重力波擴散
    total_observe_steps = 160
    for t in range(total_observe_steps):
        sim.step()
        
        # 記錄各站點的壓力變化
        for d in sensor_distances:
            p_val = float(sim.P[sim.mid, sim.mid, sim.mid + d])
            sensor_history[d].append(p_val)
            
    print("\n--- 重力波觀測站數據分析 ---")
    for d in sensor_distances:
        history = np.array(sensor_history[d])
        
        # 尋找重力場「首次回彈」突破靜態基線的瞬間
        # 靜態平衡時，遠處重力場壓力會略低於 1.0 (重力井)
        # 當重力波（回彈波前）抵達時，壓力會開始向上大幅攀升
        baseline = history[0] # 第 50 步時的靜態重力壓強
        arrival_indices = np.where(history > (baseline + 0.0005))[0]
        
        if len(arrival_indices) > 0:
            wave_time = int(arrival_indices[0])
        else:
            wave_time = total_observe_steps
            
        arrival_times.append(wave_time)
        v_g_local = d / wave_time if wave_time > 0 else 0
        print(f"觀測站 距離 R = {d} 處：重力波在湮滅後第 {wave_time:3d} 步抵達 | 湧現波速 v_g = {v_g_local:.5f} 格/步")

    # --- 線性擬合重力波時空圖 ---
    arrival_times = np.array(arrival_times)
    slope, intercept = np.polyfit(arrival_times, sensor_distances, 1)
    print("---------------------------------------")
    print(f"🏆 重力波速驗證結果：這套時空結構的重力波速 v_g = {slope:.5f} (格/步)")
    print(f"【對照組】先前測得之宇宙光速 c = 0.31544 (格/步)")
    print(f"速度自洽度 (v_g / c): { (slope / 0.31544) * 100:.2f} %")
    
    # 繪製重力波時空圖
    plt.figure(figsize=(7, 5))
    plt.plot(arrival_times, sensor_distances, 'g^-', lw=2, label='Measured Gravity Wave Front')
    plt.plot(arrival_times, slope * arrival_times + intercept, 'k--', label=f'Linear Fit (v_g={slope:.3f})')
    plt.xlabel('Time after Annihilation (Steps)')
    plt.ylabel('Distance from Source (R)')
    plt.title('Spacetime Diagram: Emergent Speed of Gravity Wave')
    plt.legend()
    plt.grid(True)
    plt.savefig('gravity_wave_speed_success.png')
    plt.show()

if __name__ == "__main__":
    run_gravity_wave_experiment()