import cupy as cp
import numpy as np
import matplotlib.pyplot as plt
import time
import csv
from energydot_engine import EnergyLatticeSim3D

def calculate_grad_norm_sq(field):
    """計算場的空間梯度模長平方 (外部觀測用)"""
    df_dz = (cp.roll(field, -1, axis=1) - cp.roll(field, 1, axis=1)) / 2.0
    df_dy = (cp.roll(field, -1, axis=2) - cp.roll(field, 1, axis=2)) / 2.0
    df_dx = (cp.roll(field, -1, axis=3) - cp.roll(field, 1, axis=3)) / 2.0
    return df_dx**2 + df_dy**2 + df_dz**2

def measure_particle(sim):
    """測量空間中的質量與幾何特徵"""
    u_mag = cp.linalg.norm(sim.u, axis=0)
    u_max = cp.max(u_mag)
    
    # 測量 R_eff (濾除低能量輻射雜訊)
    volume_mask = u_mag > 0.1  # 稍微提高雜訊閾值，避免對撞初期的碎波干擾
    V_eff = cp.sum(volume_mask)
    R_eff = (3.0 * V_eff / (4.0 * cp.pi))**(1.0 / 3.0)

    # 測量總靜止質量 m (哈密頓量積分)
    grad_norm_sq_u = calculate_grad_norm_sq(sim.u)
    grad_norm_sq_theta = calculate_grad_norm_sq(sim.theta)
    
    energy_strain_u = cp.sum(0.5 * sim.alpha * grad_norm_sq_u)
    energy_strain_theta = cp.sum(0.5 * sim.gamma * grad_norm_sq_theta)
    energy_sg_u = cp.sum(sim.beta * (1.0 - cp.cos(sim.u)))
    energy_sg_theta = cp.sum(sim.beta * (1.0 - cp.cos(sim.theta)))
    energy_skyrme_u = cp.sum(0.25 * sim.skyrme * (grad_norm_sq_u ** 2))
    energy_skyrme_theta = cp.sum(0.25 * sim.skyrme * (grad_norm_sq_theta ** 2))
    
    total_mass = (energy_strain_u + energy_strain_theta + 
                  energy_sg_u + energy_sg_theta + 
                  energy_skyrme_u + energy_skyrme_theta)

    return float(total_mass), float(R_eff), float(u_max)

def inject_colliding_waves(sim, amplitude=12.0, width=4.0, distance=15):
    """
    從外部注入兩道沒有質量的純量波，並給予相向對撞的動量。
    完全不使用 lock_mask。
    """
    z, y, x = cp.ogrid[:sim.S, :sim.S, :sim.S]
    
    # 波 1：位於中心左側，向右移動 (+z 方向)
    center1_z = sim.mid - distance
    r1 = cp.sqrt((z - center1_z)**2 + (y - sim.mid)**2 + (x - sim.mid)**2)
    pulse1 = amplitude * cp.exp(-(r1**2) / (width**2))
    
    # 前一個時間步的波 1 (位置更靠左，藉此產生向右的相速度)
    r1_prev = cp.sqrt((z - (center1_z - 1.0))**2 + (y - sim.mid)**2 + (x - sim.mid)**2)
    pulse1_prev = amplitude * cp.exp(-(r1_prev**2) / (width**2))

    # 波 2：位於中心右側，向左移動 (-z 方向)
    center2_z = sim.mid + distance
    r2 = cp.sqrt((z - center2_z)**2 + (y - sim.mid)**2 + (x - sim.mid)**2)
    pulse2 = amplitude * cp.exp(-(r2**2) / (width**2))
    
    # 前一個時間步的波 2 (位置更靠右，藉此產生向左的相速度)
    r2_prev = cp.sqrt((z - (center2_z + 1.0))**2 + (y - sim.mid)**2 + (x - sim.mid)**2)
    pulse2_prev = amplitude * cp.exp(-(r2_prev**2) / (width**2))

    # 將能量注入推擠場的 Z 軸分量 (u[0])
    sim.u[0] += pulse1 + pulse2
    sim.u_prev[0] += pulse1_prev + pulse2_prev

def run_collision_experiment():
    print("🌌 EnergyDot 創世觀測計畫：純能量對撞與粒子湧現 (Pair Production)")
    print("-" * 60)
    
    sim = EnergyLatticeSim3D(size=96)
    
    print("▶ 注入高能對撞波輻射...")
    inject_colliding_waves(sim, amplitude=15.0, width=5.0, distance=18)
    
    total_steps = 15000
    measure_interval = 100
    
    history_steps = []
    history_mass = []
    history_r_eff = []
    history_u_max = []
    
    print(f"▶ 啟動時間演化 (總步數: {total_steps})，請稍候...")
    start_time = time.time()
    
    for step in range(total_steps):
        sim.step()
        
        # 定期觀測並記錄
        if step % measure_interval == 0:
            mass, r_eff, u_max = measure_particle(sim)
            history_steps.append(step)
            history_mass.append(mass)
            history_r_eff.append(r_eff)
            history_u_max.append(u_max)
            
            # 每 1000 步印出一次進度
            if step % 1000 == 0:
                print(f"  [Step {step:5d}] 總質量: {mass:7.2f} | R_eff: {r_eff:5.2f} | 核心振幅: {u_max:5.2f}")

    elapsed = time.time() - start_time
    print("-" * 60)
    print(f"✅ 演化完成！耗時: {elapsed:.2f}s")
    print(f"🌟 最終誕生粒子基態 - 質量: {history_mass[-1]:.2f} | 幾何半徑: {history_r_eff[-1]:.2f}")
    
    # ---------------------------------------------------------
    # 匯出 CSV 檔案
    # ---------------------------------------------------------
    csv_filename = "collision_records.csv"
    print(f"💾 正在將生命週期數據寫入 {csv_filename}...")
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Step", "Total_Mass", "R_eff", "Max_Amplitude"])
        for i in range(len(history_steps)):
            writer.writerow([history_steps[i], history_mass[i], history_r_eff[i], history_u_max[i]])
            
    # ---------------------------------------------------------
    # 繪製粒子誕生時間線圖表
    # ---------------------------------------------------------
    plt.figure(figsize=(12, 5))
    
    # 圖 1: 質量演化 (The Birth of Mass)
    plt.subplot(1, 2, 1)
    plt.plot(history_steps, history_mass, color='purple', linewidth=2)
    plt.title('Emergence of Rest Mass over Time')
    plt.xlabel('Simulation Steps')
    plt.ylabel('Total Energy (Mass $m$)')
    plt.grid(True)
    
    # 圖 2: 幾何半徑演化 (The Stabilization of Volume)
    plt.subplot(1, 2, 2)
    plt.plot(history_steps, history_r_eff, color='teal', linewidth=2)
    plt.title('Stabilization of Particle Radius ($R_{eff}$)')
    plt.xlabel('Simulation Steps')
    plt.ylabel('Effective Radius ($R_{eff}$)')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('collision_evolution.png')
    print("📊 圖表已存檔為 collision_evolution.png")
    plt.show()

if __name__ == "__main__":
    run_collision_experiment()