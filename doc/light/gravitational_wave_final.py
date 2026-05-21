import cupy as cp
import numpy as np
import matplotlib.pyplot as plt

class GravityWaveSim3DGPU:
    def __init__(self, size=200, alpha=0.1):
        self.S = size
        self.alpha = alpha
        self.P = cp.ones((self.S, self.S, self.S), dtype=cp.float32)
        self.P_old = self.P.copy()
        self.mid = self.S // 2
        self.particle_exists = True

    def apply_particle_defect(self, radius=5.0):
        if self.particle_exists:
            z, y, x = cp.ogrid[:self.S, :self.S, :self.S]
            mask = ((z - self.mid)**2 + (y - self.mid)**2 + (x - self.mid)**2) <= radius**2
            self.P[mask] = 0.0

    def step(self, radius=5.0):
        self.apply_particle_defect(radius)
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

    def compute_energy_density(self):
        kin = 0.5 * (self.P - self.P_old)**2
        grad_x = (cp.roll(self.P, -1, axis=2) - cp.roll(self.P, 1, axis=2)) / 2.0
        grad_y = (cp.roll(self.P, -1, axis=1) - cp.roll(self.P, 1, axis=1)) / 2.0
        grad_z = (cp.roll(self.P, -1, axis=0) - cp.roll(self.P, 1, axis=0)) / 2.0
        pot = 0.5 * self.alpha * (grad_x**2 + grad_y**2 + grad_z**2)
        return kin + pot

def run_gravity_wave_final():
    print("最终版重力波实验：粒子湮灭 + 能量密度波前检测")
    sim = GravityWaveSim3DGPU(size=200, alpha=0.1)
    radius = 5.0
    
    print("建立静态引力井 (50步)...")
    for _ in range(50):
        sim.step(radius)
    
    # 观测距离（确保索引不越界：mid=100，最大d=90 -> 索引190 < 200）
    distances = np.array([30, 50, 70, 90], dtype=int)
    sensor_history = {d: [] for d in distances}
    
    print("💥 第50步：粒子湮灭，重力波爆发")
    sim.particle_exists = False
    total_steps = 350
    
    for t in range(total_steps):
        sim.step(radius)
        energy = sim.compute_energy_density()
        for d in distances:
            val = float(energy[sim.mid, sim.mid, sim.mid + d])
            sensor_history[d].append(val)
    
    arrival_times = []
    print("\n重力波前到达时间 (能量密度 > 1e-6):")
    for d in distances:
        hist = np.array(sensor_history[d])
        idx = np.where(hist > 1e-6)[0]
        t_arrival = idx[0] if len(idx) > 0 else total_steps
        arrival_times.append(t_arrival)
        v_local = d / t_arrival if t_arrival > 0 else 0
        print(f"距离 {d:3d} : 到达步数 {t_arrival:3d}  -> 局部波速 {v_local:.5f}")
    
    arrival_times = np.array(arrival_times)
    slope, intercept = np.polyfit(arrival_times, distances, 1)
    r2 = np.corrcoef(arrival_times, distances)[0,1]**2
    c_sim = 0.31545   # 从光速最终版测得
    
    print("\n--- 结果分析 ---")
    print(f"拟合重力波速 v_g = {slope:.5f} 格/步")
    print(f"光速 c = {c_sim:.5f} 格/步")
    print(f"比值 v_g / c = {slope / c_sim:.4f}  ({slope/c_sim*100:.2f}%)")
    print(f"理论极限 sqrt(alpha) = {np.sqrt(0.1):.5f} 格/步")
    print(f"线性度 R² = {r2:.6f}")
    
    plt.figure(figsize=(7,5))
    plt.plot(arrival_times, distances, 'g^-', lw=2, label='Gravity wave front')
    plt.plot(arrival_times, slope*arrival_times + intercept, 'k--',
             label=f'Linear fit: v_g = {slope:.4f}, R²={r2:.6f}')
    plt.xlabel('Time after annihilation (steps)')
    plt.ylabel('Distance from source (grids)')
    plt.title('Spacetime diagram of gravitational wave (final)')
    plt.legend()
    plt.grid(True)
    plt.savefig('gravity_wave_final.png')
    plt.show()

if __name__ == "__main__":
    run_gravity_wave_final()