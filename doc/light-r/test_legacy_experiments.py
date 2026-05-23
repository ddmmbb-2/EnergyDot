import cupy as cp
import numpy as np
import matplotlib.pyplot as plt
import csv
import os
from datetime import datetime
from lattice_core import EnergyLatticeSim3D

def compute_spatial_potential_energy(sim, radius):
    """
    精確計算空間形變的勢能 (剔除邊界阻尼與黑洞內部的離散雜訊)
    U = 1/2 * alpha * sum( (grad u_i)^2 )
    """
    pot = cp.zeros((sim.S, sim.S, sim.S), dtype=cp.float32)
    for i in range(3):
        grad_x = (cp.roll(sim.u[i], -1, axis=2) - cp.roll(sim.u[i], 1, axis=2)) / 2.0
        grad_y = (cp.roll(sim.u[i], -1, axis=1) - cp.roll(sim.u[i], 1, axis=1)) / 2.0
        grad_z = (cp.roll(sim.u[i], -1, axis=0) - cp.roll(sim.u[i], 1, axis=0)) / 2.0
        pot += 0.5 * sim.alpha * (grad_x**2 + grad_y**2 + grad_z**2)
        
    # 建立一個有效空間的遮罩 (Mask)
    valid_mask = cp.ones_like(pot, dtype=bool)
    
    # 1. 剔除宇宙邊緣的阻尼層 (例如外圍 20 格)
    margin = 20
    valid_mask[:margin, :, :] = False
    valid_mask[-margin:, :, :] = False
    valid_mask[:, :margin, :] = False
    valid_mask[:, -margin:, :] = False
    valid_mask[:, :, :margin] = False
    valid_mask[:, :, -margin:] = False
    
    # 2. 剔除黑洞事件視界內部的奇點雜訊 (只計算外部扭曲的空間)
    # 利用原生的 lock_mask 來判斷
    valid_mask = valid_mask & (~sim.lock_mask[0])
    
    # 只針對有效空間進行能量積分
    total_energy = float(cp.sum(pot[valid_mask]))
    return total_energy

def run_precision_mass_energy():
    print("🌌 啟動 EnergyDot 高精度質能等價實驗 (無微調，純幾何湧現)")
    
    # 1. 設定測試參數 (增加系統尺寸，確保 L >> R)
    grid_size = 160
    # 半徑即為線性尺寸 (與物理質量正比)
    test_radii = [1.0, 1.4, 1.8, 2.2, 2.6, 3.0]
    
    results = []
    
    for r in test_radii:
        print(f"\n▶ 正在生成拓撲缺陷 | 視界半徑 R = {r:.1f} ...")
        sim = EnergyLatticeSim3D(size=grid_size, mode="micro")
        
        # 為了保持第一性原理，質量設定直接與半徑連動，電荷為 0
        mass = r * 10.0 
        
        # 生成黑洞缺陷
        sim.inject_black_hole((sim.mid, sim.mid, sim.mid), mass=mass, charge=0.0, radius=r)
        
        # 演化 300 步，讓初始生成的衝擊波散去，只留下靜態引力井
        print("  等待空間幾何穩定 (300步)...", end="", flush=True)
        for _ in range(300):
            sim.step()
        print(" 完成！")
            
        # 計算嚴謹的純空間彈性勢能
        E_total = compute_spatial_potential_energy(sim, radius=r)
        
        # 記錄數據 (半徑即為質量特徵)
        results.append({
            "Radius_Mass": r,
            "Elastic_Energy": E_total
        })
        print(f"  ✨ 測得勢能 E = {E_total:.4f}")

    # --- 數據分析與自動存檔 ---
    radii = np.array([res["Radius_Mass"] for res in results])
    energies = np.array([res["Elastic_Energy"] for res in results])
    
    # 線性擬合
    slope, intercept = np.polyfit(radii, energies, 1)
    r_squared = np.corrcoef(radii, energies)[0, 1]**2
    
    # 輸出 CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"mass_energy_data_{timestamp}.csv"
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Radius (Mass Equivalent)", "Elastic Potential Energy (E)"])
        for r, e in zip(radii, energies):
            writer.writerow([r, e])
    print(f"\n💾 數據已自動儲存至: {csv_filename}")
    
    # 終端機報表
    print("\n" + "="*40)
    print("📊 實驗結果分析 (E = m c^2 湧現)")
    print("="*40)
    print(f"擬合方程式 : E = {slope:.4f} * R + ({intercept:.4f})")
    print(f"決定係數 R²: {r_squared:.6f}  (<-- 越接近 1.0 代表越完美的絕對線性)")
    if r_squared > 0.999:
        print("✅ 結論：極度完美的線性正比！我們成功消除了邊界效應。")
    else:
        print("⚠️ 結論：仍有非線性存在，請檢查 Voxel 解析度。")
    print("="*40)

    # 繪製圖表
    plt.figure(figsize=(8, 6))
    plt.plot(radii, energies, 'co-', markersize=8, linewidth=2, label='Simulation (Pure Geometric Energy)')
    plt.plot(radii, slope * radii + intercept, 'r--', linewidth=1.5, 
             label=f'Linear fit ($R^2$={r_squared:.5f})')
    
    plt.xlabel('Topological Defect Radius (Mass equivalent)')
    plt.ylabel('Total Spatially Integrated Elastic Energy (E)')
    plt.title('Emergent $E \propto m$ in 3D Vector Lattice (High Precision)')
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.7)
    
    img_filename = f"mass_energy_plot_{timestamp}.png"
    plt.savefig(img_filename, dpi=150)
    print(f"🖼️ 圖表已儲存至: {img_filename}")
    plt.show()

if __name__ == "__main__":
    run_precision_mass_energy()