import numpy as np
import matplotlib.pyplot as plt
from energy_dot_lattice_3d import EnergyLatticeSim3DGPU

def run_near_field_gravity_experiment():
    print("🚀 啟動 EnergyDot 計畫 A：近場微觀引力修正探測...")
    
    # 🔴 距離從極近 (R=10) 掃描到遠場 (R=42)
    # 在 V3 模型中，空洞半徑約為 4.5，所以 R=9 時兩個空洞剛好碰觸
    distances = np.arange(10, 44, 2)
    forces = []
    
    for r in distances:
        print(f"   正在測量間距 R = {r} (邊緣間隙 = {r - 9}) ... ", end="", flush=True)
        
        sim = EnergyLatticeSim3DGPU(size=96)
        
        # 設定空洞位置
        sim.cA_x = sim.S // 2 - r // 2
        sim.cB_x = sim.S // 2 + r // 2
        
        # 演化 900 步讓壓力場完全沉澱
        for _ in range(900):
            sim.step()
            
        f_net = sim.measure_net_force_3d()
        forces.append(f_net)
        print(f"淨推力 = {f_net:.6f}")
        
    forces = np.array(forces)
    
    # --- 理論擬合 ---
    # 我們只使用「遠場數據」(R >= 26) 來擬合牛頓 1/R^2 曲線
    # 這樣才能看出近場數據如何「偏離」古典牛頓力學
    far_field_mask = distances >= 26
    R_far = distances[far_field_mask]
    F_far = forces[far_field_mask]
    
    # 擬合常數 C，使得 F = C / R^2
    # C = 平均( F * R^2 )
    C_fit = np.mean(F_far * (R_far**2))
    
    theoretical_curve = C_fit / (distances**2)
    
    # --- 繪製近場偏離圖表 ---
    plt.figure(figsize=(10, 6))
    
    plt.plot(distances, forces, 'bo-', lw=2, label='Measured Force (V3 Lattice)')
    plt.plot(distances, theoretical_curve, 'r--', lw=2, label='Classical Newtonian limit ($1/R^2$)')
    
    # 標示出近場與遠場的分界
    plt.axvline(x=24, color='gray', linestyle=':', label='Near-field / Far-field boundary')
    
    plt.title("EnergyDot Near-Field Gravity Probe: Deviation from Newton")
    plt.xlabel("Distance between void centers (R)")
    plt.ylabel("Emergent Force")
    plt.legend()
    plt.grid(True)
    
    # 同時畫一張「殘差圖 (Residuals)」在子圖裡會更清楚，但這裡我們先看主趨勢
    plt.show()

if __name__ == "__main__":
    run_near_field_gravity_experiment()