import cupy as cp
import matplotlib.pyplot as plt
import os
import time
from lattice_core import EnergyLatticeSim3D

def run_quark_experiment():
    print("==================================================")
    print("⚛️ EnergyDot 極限微觀測試：夸克禁閉與質子湧現")
    print("==================================================")
    
    os.makedirs("quark_data", exist_ok=True)
    
    S = 128
    steps = 400
    mid = S // 2
    
    print(f"📦 初始化 3D 波動引擎 (網格大小: {S}^3)...")
    sim = EnergyLatticeSim3D(size=S, mode="micro")
    
    # ----------------------------------------------------
    # 🔺 注入三個夸克 (正三角形分佈)
    # ----------------------------------------------------
    dist = 8  # 夸克之間的初始距離
    quark_mass = 5.0
    quark_charge = 0.0  # 先不加電荷散度，純看質量與自旋的耦合
    
    # 夸克 1 (上方)
    pos1 = (mid, mid - dist, mid)
    sim.inject_particle(pos=pos1, mass=quark_mass, charge=quark_charge, spin_vector=(0, 0, 2.0), radius=3.0)
    
    # 夸克 2 (左下)
    pos2 = (mid, mid + dist, mid - dist)
    sim.inject_particle(pos=pos2, mass=quark_mass, charge=quark_charge, spin_vector=(0, 0, 2.0), radius=3.0)
    
    # 夸克 3 (右下)
    pos3 = (mid, mid + dist, mid + dist)
    sim.inject_particle(pos=pos3, mass=quark_mass, charge=quark_charge, spin_vector=(0, 0, 2.0), radius=3.0)
    
    # ----------------------------------------------------
    # ⏱️ 開始演化與數據記錄
    # ----------------------------------------------------
    print(f"\n🚀 開始 {steps} 步波動演化...")
    
    record_steps = [10, 50, 100, 200, 300, 400]
    start_time = time.time()
    
    for t in range(1, steps + 1):
        sim.step()
        
        if t % 10 == 0:
            energy_density = cp.sum(sim.u**2, axis=0)
            max_energy = float(cp.max(energy_density))
            print(f"   [Step {t:03d}/{steps}] 網格最大能量密度: {max_energy:.4f}")
            
        if t in record_steps:
            print(f"   📸 擷取 Step {t} 的 2D 切面影像...")
            energy_density = cp.sum(sim.u**2, axis=0)
            slice_2d = cp.asnumpy(energy_density[mid])
            
            plt.figure(figsize=(8, 8))
            plt.imshow(slice_2d, cmap='magma', vmin=0, vmax=float(cp.max(energy_density[mid])) * 0.8)
            plt.title(f"Quark Confinement & Proton Emergence (Step {t})\n3 Interacting Topological Defects")
            plt.axis('off')
            
            filename = f"quark_data/proton_step_{t:03d}.png"
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            plt.close()
            
    end_time = time.time()
    print(f"\n✅ 模擬完成！耗時: {end_time - start_time:.2f} 秒")
    print(f"📁 影像已儲存至 'quark_data/' 資料夾。")

if __name__ == "__main__":
    run_quark_experiment()