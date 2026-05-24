import cupy as cp
import numpy as np
import matplotlib.pyplot as plt
import time
import csv
from energydot_engine import EnergyLatticeSim3D

def calculate_grad_norm_sq(field):
    """計算場的空間梯度模長平方 ||∇f||^2 (外部觀測用)"""
    df_dz = (cp.roll(field, -1, axis=1) - cp.roll(field, 1, axis=1)) / 2.0
    df_dy = (cp.roll(field, -1, axis=2) - cp.roll(field, 1, axis=2)) / 2.0
    df_dx = (cp.roll(field, -1, axis=3) - cp.roll(field, 1, axis=3)) / 2.0
    return df_dx**2 + df_dy**2 + df_dz**2

def measure_particle(sim):
    """從外部測量模擬器中粒子的質量與半徑"""
    # ---------------------------------------------------------
    # 1. 幾何半徑測量 (Radius)
    # ---------------------------------------------------------
    u_mag = cp.linalg.norm(sim.u, axis=0)
    u_max = cp.max(u_mag)
    
    # 方法 A: 半幅半徑 R_half
    peak_idx = cp.unravel_index(cp.argmax(u_mag), u_mag.shape)
    z, y, x = cp.ogrid[:sim.S, :sim.S, :sim.S]
    dist_from_center = cp.sqrt((z - peak_idx[0])**2 + (y - peak_idx[1])**2 + (x - peak_idx[2])**2)
    
    contour_mask = (u_mag <= (u_max / 2.0) * 1.05) & (u_mag >= (u_max / 2.0) * 0.95)
    R_half = cp.mean(dist_from_center[contour_mask]) if cp.any(contour_mask) else 0.0
        
    # 方法 B: 有效球體等效半徑 R_eff
    volume_mask = u_mag > 0.05
    V_eff = cp.sum(volume_mask)
    R_eff = (3.0 * V_eff / (4.0 * cp.pi))**(1.0 / 3.0)

    # ---------------------------------------------------------
    # 2. 靜止質量測量 (Total Rest Mass / Hamiltonian)
    # ---------------------------------------------------------
    grad_norm_sq_u = calculate_grad_norm_sq(sim.u)
    grad_norm_sq_theta = calculate_grad_norm_sq(sim.theta)
    
    # 提取宇宙常數
    alpha, gamma = sim.alpha, sim.gamma
    beta, skyrme = sim.beta, sim.skyrme
    
    # a. 應變動能
    energy_strain_u = cp.sum(0.5 * alpha * grad_norm_sq_u)
    energy_strain_theta = cp.sum(0.5 * gamma * grad_norm_sq_theta)
    
    # b. Sine-Gordon 勢能
    energy_sg_u = cp.sum(beta * (1.0 - cp.cos(sim.u)))
    energy_sg_theta = cp.sum(beta * (1.0 - cp.cos(sim.theta)))
    
    # c. Skyrme 剛性能
    energy_skyrme_u = cp.sum(0.25 * skyrme * (grad_norm_sq_u ** 2))
    energy_skyrme_theta = cp.sum(0.25 * skyrme * (grad_norm_sq_theta ** 2))
    
    total_mass = (energy_strain_u + energy_strain_theta + 
                  energy_sg_u + energy_sg_theta + 
                  energy_skyrme_u + energy_skyrme_theta)

    return float(total_mass), float(R_half), float(R_eff)

def run_experiment():
    print("🌌 EnergyDot 宇宙驗證計畫啟動：驗證 m ∝ R")
    print("-" * 50)
    
    # 測試不同的初始拓撲缺陷半徑
    test_radii = [3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    relaxation_steps = 5000  # 讓系統演化至基態的步數
    
    # 用於儲存 CSV 記錄的資料結構
    csv_data = []
    
    results_mass = []
    results_r_half = []
    results_r_eff = []
    
    for r in test_radii:
        print(f"▶ 正在生成初始半徑 r={r} 的粒子並進行淬鍊...")
        start_time = time.time()
        
        # 1. 創世：初始化晶格宇宙
        sim = EnergyLatticeSim3D(size=96)
        center = (sim.mid, sim.mid, sim.mid)
        
        # 2. 注入拓撲死結
        sim.inject_black_hole(pos=center, mass=10.0, charge=0.0, radius=r)
        
        # 3. 能量極小化 (Relaxation)：讓晶格力學自行決定完美體積
        for step in range(relaxation_steps):
            sim.step()
            
        # 4. 外部測量
        mass, r_half, r_eff = measure_particle(sim)
        
        # 記錄至陣列供畫圖使用
        results_mass.append(mass)
        results_r_half.append(r_half)
        results_r_eff.append(r_eff)
        
        # 記錄至陣列供 CSV 輸出使用
        csv_data.append([r, mass, r_half, r_eff])
        
        elapsed = time.time() - start_time
        print(f"  └ 完成! 耗時: {elapsed:.2f}s | 質量 m: {mass:.2f} | R_half: {r_half:.2f} | R_eff: {r_eff:.2f}")

    print("-" * 50)
    
    # ---------------------------------------------------------
    # 匯出 CSV 檔案
    # ---------------------------------------------------------
    csv_filename = "mass_radius_records.csv"
    print(f"💾 正在將實驗數據寫入 {csv_filename}...")
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Initial_Radius_r", "Rest_Mass_m", "R_half", "R_eff"])
        writer.writerows(csv_data)
        
    print("📊 實驗完成，正在繪製結果...")
    
    # ---------------------------------------------------------
    # 繪製驗證圖表
    # ---------------------------------------------------------
    plt.figure(figsize=(10, 5))
    
    # 圖 1: Mass vs R_half
    plt.subplot(1, 2, 1)
    plt.plot(results_r_half, results_mass, marker='o', linestyle='-', color='b')
    plt.title('Rest Mass vs Half-Amplitude Radius ($R_{half}$)')
    plt.xlabel('Radius ($R_{half}$)')
    plt.ylabel('Total Energy (Mass $m$)')
    plt.grid(True)
    
    # 圖 2: Mass vs R_eff
    plt.subplot(1, 2, 2)
    plt.plot(results_r_eff, results_mass, marker='s', linestyle='-', color='r')
    plt.title('Rest Mass vs Effective Radius ($R_{eff}$)')
    plt.xlabel('Radius ($R_{eff}$)')
    plt.ylabel('Total Energy (Mass $m$)')
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('mass_radius_validation.png')
    plt.show()

if __name__ == "__main__":
    run_experiment()