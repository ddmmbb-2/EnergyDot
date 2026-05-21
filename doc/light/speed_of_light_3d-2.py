import cupy as cp
import numpy as np
import matplotlib.pyplot as plt

class LightSpeedSim3DGPU:
    def __init__(self, size=200, alpha=0.1):
        self.S = size
        self.alpha = alpha
        self.P = cp.ones((self.S, self.S, self.S), dtype=cp.float32)
        self.P_old = self.P.copy()
        self.mid = self.S // 2

    def inject_pulse(self):
        self.P[self.mid, self.mid, self.mid] = 10.0

    def step(self):
        P_up    = cp.roll(self.P,  1, axis=1)
        P_down  = cp.roll(self.P, -1, axis=1)
        P_left  = cp.roll(self.P,  1, axis=2)
        P_right = cp.roll(self.P, -1, axis=2)
        P_front = cp.roll(self.P,  1, axis=0)
        P_back  = cp.roll(self.P, -1, axis=0)
        laplacian = (P_up + P_down + P_left + P_right + P_front + P_back - 6 * self.P)
        P_next = 2 * self.P - self.P_old + self.alpha * laplacian
        self.P_old = self.P.copy()
        self.P = P_next

def run_light_speed_final():
    print("=== 最终版光速实验：单点脉冲 + 压力前缘检测 ===")
    sim = LightSpeedSim3DGPU(size=200, alpha=0.1)
    sim.inject_pulse()
    
    distances = np.array([30, 50, 70, 90], dtype=int)
    sensor_history = {d: [] for d in distances}
    total_steps = 350
    
    for t in range(total_steps):
        for d in distances:
            val = float(sim.P[sim.mid, sim.mid, sim.mid + d])
            sensor_history[d].append(val)
        sim.step()
    
    arrival_times = []
    print("\n波前到达时间 (压力 > 1.0005):")
    for d in distances:
        hist = np.array(sensor_history[d])
        idx = np.where(hist > 1.0005)[0]
        t_arrival = idx[0] if len(idx) > 0 else total_steps
        arrival_times.append(t_arrival)
        v_local = d / t_arrival
        print(f"距离 {d:3d} : 到达步数 {t_arrival:3d}  -> 局部光速 {v_local:.5f}")
    
    arrival_times = np.array(arrival_times)
    slope, intercept = np.polyfit(arrival_times, distances, 1)
    r2 = np.corrcoef(arrival_times, distances)[0,1]**2
    c_theory = np.sqrt(0.1)
    print(f"\n拟合光速 c = {slope:.5f}  格/步")
    print(f"理论极限 sqrt(alpha) = {c_theory:.5f}  格/步")
    print(f"相对误差 = {abs(slope - c_theory)/c_theory*100:.3f}%")
    print(f"线性度 R² = {r2:.6f}")
    
    plt.figure(figsize=(7,5))
    plt.plot(arrival_times, distances, 'ro-', lw=2, label='Pressure front')
    plt.plot(arrival_times, slope*arrival_times + intercept, 'k--', 
             label=f'c = {slope:.4f}, R²={r2:.6f}')
    plt.xlabel('Time (steps)')
    plt.ylabel('Distance (grids)')
    plt.title('Final: Speed of Light in Elastic Lattice')
    plt.legend()
    plt.grid(True)
    plt.savefig('speed_of_light_final.png')
    plt.show()

if __name__ == "__main__":
    run_light_speed_final()