import cupy as cp
import numpy as np
import matplotlib.pyplot as plt

class SolitonCollisionSim:
    def __init__(self, size=200):
        self.S = size
        self.u = cp.zeros((size, size), dtype=cp.float32)
        self.u_prev = cp.zeros((size, size), dtype=cp.float32)
        
        self.alpha = 0.1  # 空間傳遞速率
        self.beta = 0.05  # 非線性束縛力 (維持粒子形狀)
        
        # 建立一面「無限大質量的牆壁」
        self.wall_mask = cp.zeros((size, size), dtype=bool)
        # 牆壁設在 X=120 的位置，厚度為 5 格
        self.wall_mask[:, 120:125] = True

    def inject_moving_soliton(self, start_pos, radius=4.0, velocity_x=0.0):
        y, x = cp.ogrid[:self.S, :self.S]
        dy, dx = y - start_pos[0], x - start_pos[1]
        dist = cp.sqrt(dx**2 + dy**2)
        
        amplitude = 3.14159 
        pulse = amplitude * cp.exp(-(dist**2) / (radius**2))
        
        self.u = pulse
        
        dx_prev = x - (start_pos[1] - velocity_x)
        dist_prev = cp.sqrt(dx_prev**2 + dy**2)
        pulse_prev = amplitude * cp.exp(-(dist_prev**2) / (radius**2))
        
        self.u_prev = pulse_prev

    def step(self):
        u_up    = cp.roll(self.u,  1, axis=0)
        u_down  = cp.roll(self.u, -1, axis=0)
        u_left  = cp.roll(self.u,  1, axis=1)
        u_right = cp.roll(self.u, -1, axis=1)
        
        laplacian = u_up + u_down + u_left + u_right - 4 * self.u
        
        u_next = 2 * self.u - self.u_prev + self.alpha * laplacian - self.beta * cp.sin(self.u)
        
        # 邊界阻尼 (只放在上下邊緣和最左邊，右邊有牆)
        margin = 10
        y, x = cp.ogrid[:self.S, :self.S]
        mask_edge = (x < margin) | (y < margin) | (y >= self.S - margin)
        u_next = cp.where(mask_edge, u_next * 0.95, u_next)
        
        # 🔴 撞牆處理：強制將牆壁區域的波幅壓平 (固定邊界條件)
        u_next = cp.where(self.wall_mask, 0.0, u_next)
        
        self.u_prev = self.u.copy()
        self.u = u_next

def run_collision_test():
    print("💥 啟動 EnergyDot：非線性波包撞牆實驗")
    
    sim = SolitonCollisionSim(size=150)
    
    # 起點稍微近一點，速度快一點，讓它趕快撞上
    start_y, start_x = 75, 40
    initial_velocity = 1.5
    
    print(f"發射粒子！起點: ({start_y}, {start_x}), 準備撞擊 X=120 的牆壁...")
    sim.inject_moving_soliton((start_y, start_x), radius=4.0, velocity_x=initial_velocity)
    
    # 紀錄撞擊前、撞擊中、撞擊後的快照
    snapshots = {}
    record_steps = [0, 45, 65, 110]
    
    for t in range(max(record_steps) + 1):
        if t in record_steps:
            snapshots[t] = cp.asnumpy(sim.u)
        sim.step()
        
    # --- 繪圖 ---
    fig, axes = plt.subplots(1, len(record_steps), figsize=(16, 4))
    
    # 取得牆壁的 X 座標範圍用於畫線
    wall_x_start = 120
    
    for i, t in enumerate(record_steps):
        ax = axes[i]
        c = ax.pcolormesh(snapshots[t], cmap='magma', vmin=-1.5, vmax=3.2)
        ax.set_title(f'Time Step: {t}')
        ax.set_xlabel('X axis')
        if i == 0:
            ax.set_ylabel('Y axis')
            
        # 畫出那面牆壁 (用紅色虛線標示)
        ax.axvline(x=wall_x_start, color='red', linestyle='--', linewidth=2, alpha=0.7)
        
        # 找出波包中心 (取絕對值最大處，因為反彈可能會變負的)
        peak_idx = np.unravel_index(np.argmax(np.abs(snapshots[t])), snapshots[t].shape)
        peak_y, peak_x = peak_idx
        
        # 只有當波包有一定強度時才畫 X (避免波完全碎掉時亂畫)
        if np.abs(snapshots[t][peak_y, peak_x]) > 0.5:
            ax.plot(peak_x, peak_y, color='cyan', marker='x', markersize=10)
        
    plt.tight_layout()
    plt.savefig('soliton_collision.png', dpi=150)
    print("🖼️ 撞擊軌跡圖已儲存至: soliton_collision.png")
    plt.show()

if __name__ == "__main__":
    run_collision_test()