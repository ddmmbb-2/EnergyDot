import cupy as cp
import matplotlib.pyplot as plt
import os
import time
from lattice_core import EnergyLatticeSim3D

def run_blackhole_experiment():
    print("==================================================")
    print("🌌 EnergyDot 終極極限測試：黑洞與真空漲落")
    print("==================================================")
    
    # 建立數據儲存資料夾
    os.makedirs("blackhole_data", exist_ok=True)
    
    # 設定晶格大小 (建議至少 128 以觀察波的傳遞)
    S = 128
    steps = 400  # 演化步數，可以調長觀察長時間效應
    
    print(f"📦 初始化 3D 波動引擎 (網格大小: {S}^3)...")
    sim = EnergyLatticeSim3D(size=S, mode="micro")
    
    # ----------------------------------------------------
    # 🕳️ 黑洞參數設定
    # ----------------------------------------------------
    bh_pos = (S//2, S//2, S//2)
    # 極端質量 (純量排擠)
    bh_mass = 150.0  
    # 極端電荷 (徑向散度) - 這是抵抗崩潰的關鍵
    bh_charge = 100.0 
    # 視界半徑
    bh_radius = 12.0 
    
    print("\n⚠️ 正在注入雷斯納-諾德斯特洛姆(Reissner-Nordström) 極端黑洞...")
    sim.inject_black_hole(pos=bh_pos, mass=bh_mass, charge=bh_charge, radius=bh_radius)
    
    # ----------------------------------------------------
    # ⏱️ 開始演化與數據記錄
    # ----------------------------------------------------
    print(f"\n🚀 開始 {steps} 步波動演化 (引入真空漲落)...")
    
    # 記錄切面能量密度的陣列 (取 Z 軸正中央切面)
    # 只存特定時間點以節省記憶體
    record_steps = [10, 50, 100, 200, 300, 400]
    
    start_time = time.time()
    
    for t in range(1, steps + 1):
        sim.step()
        
        # 每 10 步印出一次進度
        if t % 10 == 0:
            # 監測中央切面的最大能量，確保數值沒有爆炸 (NaN)
            energy_density = cp.sum(sim.u**2, axis=0)
            max_energy = float(cp.max(energy_density))
            print(f"   [Step {t:03d}/{steps}] 網格最大能量密度: {max_energy:.4f}")
            
        # 記錄特定時間點的切面圖
        if t in record_steps:
            print(f"   📸 擷取 Step {t} 的 2D 切面影像...")
            energy_density = cp.sum(sim.u**2, axis=0)
            slice_2d = cp.asnumpy(energy_density[S//2])
            
            plt.figure(figsize=(8, 8))
            # 使用 vmin 和 vmax 鎖定顏色範圍，讓對比度更強，凸顯微弱的輻射波
            plt.imshow(slice_2d, cmap='inferno', vmin=0, vmax=0.5)
            
            # 畫出事件視界 (黑洞邊界)
            circle = plt.Circle((S//2, S//2), bh_radius, color='cyan', fill=False, linestyle='--', linewidth=1.5, label='Event Horizon')
            plt.gca().add_patch(circle)
            
            plt.title(f"Black Hole Boundary Fluctuations (Step {t})\nMass={bh_mass}, Charge={bh_charge}")
            plt.axis('off')
            plt.legend(loc='upper right')
            
            # 儲存影像
            filename = f"blackhole_data/bh_step_{t:03d}.png"
            plt.savefig(filename, dpi=150, bbox_inches='tight')
            plt.close()
            
    end_time = time.time()
    print(f"\n✅ 模擬完成！耗時: {end_time - start_time:.2f} 秒")
    print(f"📁 影像已儲存至 'blackhole_data/' 資料夾。")

if __name__ == "__main__":
    run_blackhole_experiment()