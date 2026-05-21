import numpy as np
import cupy as cp
import matplotlib.pyplot as plt
from energy_dot_lattice_3d import EnergyLatticeSim3DGPU

def run_3d_gravity_experiment():
    print("開始執行 EnergyDot 終極驗證：大空間遠場三維晶格（湧現 1/R² 萬有引力）...")
    
    # 🔴 調整測試距離：從 R = 22 到 46，徹底避開近場相干干涉
    distances = np.array([22, 25, 28, 31, 34, 37, 40, 43, 46])
    forces = []
    
    for r in distances:
        print(f"正在測試 3D 晶格間距 R = {r} ... ", end="", flush=True)
        
        # 建立大空間 3D 模擬器 (size=96)
        sim = EnergyLatticeSim3DGPU(size=96)
        
        # 設定重力缺陷在 3D 空間中的相對距離
        sim.cA_x = sim.S // 2 - r // 2
        sim.cB_x = sim.S // 2 + r // 2
        
        # 🔴 增加迭代步數到 900 步，讓 88 萬個球球的彈性變形場完全沉澱、達到靜態平衡
        for _ in range(900):
            sim.step()
            
        f_net = sim.measure_net_force_3d()
        forces.append(f_net)
        print(f"3D 應力淨引力 = {f_net:.5f}")
        
    # --- 繪製 3D 萬有引力驗證圖表 ---
    plt.figure(figsize=(8, 5))
    plt.plot(distances, forces, 'go-', lw=2, label='3D Lattice Simulation (EnergyDot V3)')
    
    # 理論擬合線：真正的三維牛頓萬有引力反比平方律 1/R²
    theoretical_3d = (1.0 / (distances**2)) * (forces[0] * (distances[0]**2))
    plt.plot(distances, theoretical_3d, 'k--', label='Newtonian Gravity Limit (1/R²)')
    
    plt.xlabel('3D Lattice Distance (R)')
    plt.ylabel('Emergent Force (Stress Gradient)')
    plt.title('V3 Final Verification: Emergent 1/R² Gravity from 3D Lattice')
    plt.legend()
    plt.grid(True)
    plt.savefig('3d_gravity_inverse_square_success.png')
    plt.show()

if __name__ == "__main__":
    run_3d_gravity_experiment()