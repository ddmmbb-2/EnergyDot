import cupy as cp
import numpy as np
import pandas as pd
import time
from energydot_engine import EnergyLatticeSim3D

def calculate_strain_energy(u_field):
    """
    計算晶格的總彈性應變能 (Elastic Strain Energy)
    根據第一性原理，能量是空間形變的勢能： E ∝ Σ (∇u)²
    """
    energy = 0.0
    # u_field 維度為 (3, S, S, S)，分別對應 x, y, z 分量
    for component in range(3):
        # 取得單一分量的 3D 空間張量
        field = u_field[component]
        
        # 使用 CuPy 計算三個空間軸的梯度 (差分)
        grad_z, grad_y, grad_x = cp.gradient(field)
        
        # 應變能密度為梯度的平方
        energy_density = grad_x**2 + grad_y**2 + grad_z**2
        
        # 將全空間的能量密度積分 (加總)
        energy += float(cp.sum(energy_density))
        
    return energy

def run_mass_radius_validation():
    print("🌌 EnergyDot 宇宙驗證啟動：質量的拓撲本質")
    print("-" * 50)
    
    # 實驗參數設定
    sim_size = 96
    mass_list = [10.0, 20.0, 30.0, 40.0, 50.0]
    radius_list = [2.0, 4.0, 6.0, 8.0, 10.0]
    
    results = []
    
    total_experiments = len(mass_list) * len(radius_list)
    current_exp = 1

    # 進行雙參數掃描 (Sweep)
    for r in radius_list:
        for m in mass_list:
            print(f"[{current_exp}/{total_experiments}] 正在注入黑洞... 質量 m={m}, 半徑 R={r}")
            start_time = time.time()
            
            # 1. 實例化宇宙晶格 (每次實驗重置真空)
            sim = EnergyLatticeSim3D(size=sim_size, mode="micro")
            
            # 2. 注入拓撲缺陷 (不帶自旋以純化應變能計算)
            center = (sim.mid, sim.mid, sim.mid)
            sim.inject_black_hole(pos=center, mass=m, charge=0, radius=r, spin_vector=(0.0, 0.0, 0.0))
            
            # 3. 讓宇宙演化幾步，讓邊界應力釋放並穩定 (可選)
            for _ in range(5):
                sim.step()
                
            # 4. 測量該拓撲缺陷所儲存的總彈性應變能
            total_energy = calculate_strain_energy(sim.u)
            
            # 理論預測值計算 (供參考) : E ∝ m² / R
            theoretical_ratio = (m**2) / r
            
            results.append({
                "Mass_(m)": m,
                "Radius_(R)": r,
                "Strain_Energy_(E)": total_energy,
                "Theoretical_m2_over_R": theoretical_ratio
            })
            
            current_exp += 1
            cp.get_default_memory_pool().free_all_blocks() # 釋放 GPU 記憶體避免溢位

    print("-" * 50)
    print("✅ 模擬完成！正在將數據匯出至 CSV...")
    
    # 儲存為 CSV
    df = pd.DataFrame(results)
    csv_filename = "energydot_validation_results.csv"
    df.to_csv(csv_filename, index=False)
    print(f"📁 數據已儲存至：{csv_filename}")
    
if __name__ == "__main__":
    run_mass_radius_validation()