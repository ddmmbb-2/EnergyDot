import cupy as cp
import matplotlib.pyplot as plt
import os
import time
from lattice_core import EnergyLatticeSim3D

def run_long_quark_experiment():
    print("==================================================")
    print("⚛️ 質子終極壽命測試：2000步無反射模擬")
    print("==================================================")
    
    os.makedirs("quark_data_long", exist_ok=True)
    
    # 微幅擴大宇宙到 S=200，讓波紋有更多空間伸展
    S = 200
    steps = 2000
    mid = S // 2
    
    print(f"📦 初始化 3D 波動引擎 (網格大小: {S}^3，已啟用吸收邊界)...")
    sim = EnergyLatticeSim3D(size=S, mode="micro")
    
    # 注入三個夸克
    dist = 8
    quark_mass = 5.0
    
    pos1 = (mid, mid - dist, mid)
    pos2 = (mid, mid + dist, mid - dist)
    pos3 = (mid, mid + dist, mid + dist)
    
    sim.inject_particle(pos=pos1, mass=quark_mass, charge=0.0, spin_vector=(0, 0, 2.0), radius=3.0)
    sim.inject_particle(pos=pos2, mass=quark_mass, charge=0.0, spin_vector=(0, 0, 2.0), radius=3.0)
    sim.inject_particle(pos=pos3, mass=quark_mass, charge=0.0, spin_vector=(0, 0, 2.0), radius=3.0)
    
    print(f"\n🚀 開始 {steps} 步長效演化...")
    
    # 記錄每一步的最大能量，用來畫壽命曲線
    energy_history = []
    record_steps = [100, 500, 1000, 1500, 2000]
    
    start_time = time.time()
    
    for t in range(1, steps + 1):
        sim.step()
        
        # 追蹤中心區域 (質子本體) 的最大能量密度
        energy_density = cp.sum(sim.u**2, axis=0)
        max_energy = float(cp.max(energy_density))
        energy_history.append(max_energy)
        
        if t % 100 == 0:
            print(f"   [Step {t:04d}/{steps}] 網格最大能量密度: {max_energy:.4f}")
            
        if t in record_steps:
            slice_2d = cp.asnumpy(energy_density[mid])
            plt.figure(figsize=(8, 8))
            plt.imshow(slice_2d, cmap='magma', vmin=0, vmax=max_energy * 0.8)
            plt.title(f"Proton Stability Test (Step {t})")
            plt.axis('off')
            plt.savefig(f"quark_data_long/proton_step_{t:04d}.png", dpi=150, bbox_inches='tight')
            plt.close()
            
    # --- 繪製終極證明：能量壽命曲線 ---
    print("\n📊 正在繪製質子能量壽命曲線...")
    plt.figure(figsize=(10, 5))
    plt.plot(range(1, steps + 1), energy_history, color='purple', linewidth=2)
    plt.title("Proton Core Energy Density vs. Time")
    plt.xlabel("Simulation Steps")
    plt.ylabel("Max Energy Density")
    plt.yscale('log') # 使用對數坐標，看得更清楚
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig("quark_data_long/proton_energy_curve.png", dpi=300, bbox_inches='tight')
    plt.close()

    end_time = time.time()
    print(f"✅ 模擬完成！耗時: {end_time - start_time:.2f} 秒")
    print(f"📁 影像與數據曲線已儲存至 'quark_data_long/' 資料夾。")

if __name__ == "__main__":
    run_long_quark_experiment()