import cupy as cp
import numpy as np
import matplotlib.pyplot as plt
from lattice_core import EnergyLatticeSim3D

def compute_micropolar_energy_density(sim):
    """計算大一統框架下的總能量密度 (推擠 + 自旋)"""
    kin_u = 0.5 * cp.sum((sim.u - sim.u_prev)**2, axis=0)
    kin_theta = 0.5 * cp.sum((sim.theta - sim.theta_prev)**2, axis=0)
    
    pot_u = cp.zeros_like(kin_u)
    pot_theta = cp.zeros_like(kin_theta)
    
    for i in range(3):
        # 推擠勢能
        gu_x = (cp.roll(sim.u[i], -1, axis=2) - cp.roll(sim.u[i], 1, axis=2)) / 2.0
        gu_y = (cp.roll(sim.u[i], -1, axis=1) - cp.roll(sim.u[i], 1, axis=1)) / 2.0
        gu_z = (cp.roll(sim.u[i], -1, axis=0) - cp.roll(sim.u[i], 1, axis=0)) / 2.0
        pot_u += 0.5 * sim.alpha * (gu_x**2 + gu_y**2 + gu_z**2)
        
        # 扭轉勢能
        gt_x = (cp.roll(sim.theta[i], -1, axis=2) - cp.roll(sim.theta[i], 1, axis=2)) / 2.0
        gt_y = (cp.roll(sim.theta[i], -1, axis=1) - cp.roll(sim.theta[i], 1, axis=1)) / 2.0
        gt_z = (cp.roll(sim.theta[i], -1, axis=0) - cp.roll(sim.theta[i], 1, axis=0)) / 2.0
        pot_theta += 0.5 * sim.gamma * (gt_x**2 + gt_y**2 + gt_z**2)
        
    return kin_u + kin_theta + pot_u + pot_theta

def run_light_speed_test():
    print("\n=== 實驗 1：光速測量 (Micropolar Field) ===")
    sim = EnergyLatticeSim3D(size=200, mode="micro")
    sim.u[:, sim.mid, sim.mid, sim.mid] = 10.0
    
    distances = np.array([30, 50, 70, 90], dtype=int)
    sensor_history = {d: [] for d in distances}
    total_steps = 400
    
    for t in range(total_steps):
        for d in distances:
            val = float(cp.linalg.norm(sim.u[:, sim.mid, sim.mid, sim.mid + d]))
            sensor_history[d].append(val)
        sim.step()
    
    arrival_times = []
    print("波前到達時間 (位移強度 > 1e-4):")
    for d in distances:
        hist = np.array(sensor_history[d])
        idx = np.where(hist > 1e-4)[0]
        t_arrival = idx[0] if len(idx) > 0 else total_steps
        
        # 🔴 剛剛就是漏了這一行，導致陣列是空的！
        arrival_times.append(t_arrival) 
        
        v_local = d / t_arrival if t_arrival > 0 else 0
        print(f"距離 {d:3d} : 到達步数 {t_arrival:3d}  -> 局部波速 {v_local:.5f}")
    
    arrival_times = np.array(arrival_times)
    slope, intercept = np.polyfit(arrival_times, distances, 1)
    c_theory = np.sqrt(sim.alpha)
    print(f"\n擬合光速 c = {slope:.5f} 格/步 (理論極限={c_theory:.5f})")

def run_gravitational_wave_test():
    print("\n=== 實驗 2：重力波爆發 (粒子湮滅) ===")
    sim = EnergyLatticeSim3D(size=200, mode="micro")
    
    print("建立靜態引力井 (等待 50 步)...")
    sim.inject_black_hole((sim.mid, sim.mid, sim.mid), mass=50.0, charge=0.0, radius=5.0)
    for _ in range(50):
        sim.step()
    
    distances = np.array([30, 50, 70, 90], dtype=int)
    sensor_history = {d: [] for d in distances}
    
    print("💥 第 50 步：解除鎖定遮罩 (粒子湮滅)！")
    sim.lock_mask.fill(False)
    
    total_steps = 350
    for t in range(total_steps):
        sim.step()
        energy = compute_micropolar_energy_density(sim)
        for d in distances:
            val = float(energy[sim.mid, sim.mid, sim.mid + d])
            sensor_history[d].append(val)
            
    print("\n重力波前到達時間 (能量密度 > 1e-5):")
    for d in distances:
        hist = np.array(sensor_history[d])
        idx = np.where(hist > 1e-5)[0]
        t_arrival = idx[0] if len(idx) > 0 else total_steps
        v_local = d / t_arrival if t_arrival > 0 else 0
        print(f"距離 {d:3d} : 到達步数 {t_arrival:3d}  -> 局部波速 {v_local:.5f}")

if __name__ == "__main__":
    run_light_speed_test()
    run_gravitational_wave_test()