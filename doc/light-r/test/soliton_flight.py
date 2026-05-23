import cupy as cp
import numpy as np
import matplotlib.pyplot as plt

class SolitonFlightSim:
    def __init__(self, size=200):
        self.S = size
        self.mid = size // 2
        
        # 為了視覺化清晰，我們這次使用單一純量場來模擬波包飛行
        self.u = cp.zeros((size, size), dtype=cp.float32)
        self.u_prev = cp.zeros((size, size), dtype=cp.float32)
        
        self.alpha = 0.1  # 空間傳遞速率
        self.beta = 0.05  # 非線性束縛力 (Sine-Gordon 係數)

    def inject_moving_soliton(self, start_pos, radius=5.0, velocity_x=0.0):
        """注入一個帶有初始速度的拓撲孤子 (波包)"""
        y, x = cp.ogrid[:self.S, :self.S]
        dy, dx = y - start_pos[0], x - start_pos[1]
        
        dist = cp.sqrt(dx**2 + dy**2)
        
        # 使用高斯分佈來模擬一個集中的波包
        amplitude = 3.14159  # 在 Sine-Gordon 中，pi 是一個拓撲翻轉的關鍵值
        pulse = amplitude * cp.exp(-(dist**2) / (radius**2))
        
        self.u = pulse
        
        # 關鍵：如何給予初始速度？
        # 我們讓 u_prev 在 X 軸上稍微「落後」一點，這樣波就會產生向前的慣性！
        # 位移量約為 velocity_x * dt (這裡 dt=1)
        dx_prev = x - (start_pos[1] - velocity_x)
        dist_prev = cp.sqrt(dx_prev**2 + dy**2)
        pulse_prev = amplitude * cp.exp(-(dist_prev**2) / (radius**2))
        
        self.u_prev = pulse_prev

    def step(self):
        """非線性波動方程式演化"""
        u_up    = cp.roll(self.u,  1, axis=0)
        u_down  = cp.roll(self.u, -1, axis=0)
        u_left  = cp.roll(self.u,  1, axis=1)
        u_right = cp.roll(self.u, -1, axis=1)
        
        laplacian = u_up + u_down + u_left + u_right - 4 * self.u
        
        # 加入 Sine-Gordon 非線性束縛項： - beta * sin(u)
        u_next = 2 * self.u - self.u_prev + self.alpha * laplacian - self.beta * cp.sin(self.u)
        
        # 吸收邊界條件 (防止撞牆反彈干擾)
        margin = 10
        y, x = cp.ogrid[:self.S, :self.S]
        mask_edge = (x < margin) | (x >= self.S - margin) | (y < margin) | (y >= self.S - margin)
        u_next = cp.where(mask_edge, u_next * 0.95, u_next)
        
        self.u_prev = self.u.copy()
        self.u = u_next

def run_flight_test():
    print("🚀 啟動 EnergyDot：非線性孤子 (波包) 自由飛行實驗")
    
    sim = SolitonFlightSim(size=150)
    
    # 把它放在畫面左側，並給予向右的初始速度
    start_y, start_x = 75, 30
    initial_velocity = 1.2
    
    print(f"注入孤子... 起點: ({start_y}, {start_x}), 初速: {initial_velocity}")
    sim.inject_moving_soliton((start_y, start_x), radius=4.0, velocity_x=initial_velocity)
    
    # 紀錄幾張特定時間點的快照
    snapshots = {}
    record_steps = [0, 40, 80, 120]
    
    print("讓粒子飛！演化中...")
    for t in range(max(record_steps) + 1):
        if t in record_steps:
            snapshots[t] = cp.asnumpy(sim.u)
        sim.step()
        
    # --- 繪製連拍軌跡圖 ---
    fig, axes = plt.subplots(1, len(record_steps), figsize=(16, 4))
    
    for i, t in enumerate(record_steps):
        ax = axes[i]
        # 畫出熱力圖
        c = ax.pcolormesh(snapshots[t], cmap='magma', vmin=0, vmax=3.2)
        ax.set_title(f'Time Step: {t}')
        ax.set_xlabel('X axis')
        if i == 0:
            ax.set_ylabel('Y axis')
        
        # 找出波包目前的中心位置 (峰值) 並標示
        peak_y, peak_x = np.unravel_index(np.argmax(snapshots[t]), snapshots[t].shape)
        ax.plot(peak_x, peak_y, color='cyan', marker='x', markersize=10)
        
    plt.tight_layout()
    plt.savefig('soliton_flight_trajectory.png', dpi=150)
    print("🖼️ 孤子飛行軌跡圖已儲存至: soliton_flight_trajectory.png")
    plt.show()

if __name__ == "__main__":
    run_flight_test()