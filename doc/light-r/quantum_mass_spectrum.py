import cupy as cp
import numpy as np
import matplotlib.pyplot as plt
import csv
from datetime import datetime
from lattice_core import EnergyLatticeSim3D

def compute_spatial_potential_energy(sim):
    """計算純粹空間形變的勢能 (避開邊界與內部雜訊)"""
    pot = cp.zeros((sim.S, sim.S, sim.S), dtype=cp.float32)
    for i in range(3):
        grad_x = (cp.roll(sim.u[i], -1, axis=2) - cp.roll(sim.u[i], 1, axis=2)) / 2.0
        grad_y = (cp.roll(sim.u[i], -1, axis=1) - cp.roll(sim.u[i], 1, axis=1)) / 2.0
        grad_z = (cp.roll(sim.u[i], -1, axis=0) - cp.roll(sim.u[i], 1, axis=0)) / 2.0
        pot += 0.5 * sim.alpha * (grad_x**2 + grad_y**2 + grad_z**2)
        
    valid_mask = cp.ones_like(pot, dtype=bool)
    
    # 邊界阻尼層設定較小，因為整體 size=64
    margin = 10
    valid_mask[:margin, :, :] = False
    valid_mask[-margin:, :, :] = False
    valid_mask[:, :margin, :] = False
    valid_mask[:, -margin:, :] = False
    valid_mask[:, :, :margin] = False
    valid_mask[:, :, -margin:] = False
    
    # 剔除事件視界內部
    valid_mask = valid_mask & (~sim.lock_mask[0])
    return float(cp.sum(pot[valid_mask]))

def run_quantum_mass_spectrum():
    print("⚛️ 啟動 EnergyDot 微觀測量：粒子的量子質量譜掃描")
    
    # 高解析度半徑掃描：從 0.5 到 3.2，間距 0.05
    test_radii = np.arange(0.5, 3.25, 0.05)
    energies = []
    
    # 計算理論的晶格躍遷點 (sqrt(1), sqrt(2), sqrt(3)...)
    lattice_distances = [np.sqrt(i) for i in range(1, 11)]
    
    print(f"總共需要掃描 {len(test_radii)} 個微觀半徑...")
    
    for r in test_radii:
        sim = EnergyLatticeSim3D(size=64, mode="micro")
        
        # 質量參數我們依然保持線性綁定
        mass = r * 10.0 
        sim.inject_black_hole((sim.mid, sim.mid, sim.mid), mass=mass, charge=0.0, radius=r)
        
        # 微觀尺度下，演化 150 步即足以讓近場空間穩定
        for _ in range(150):
            sim.step()
            
        E_total = compute_spatial_potential_energy(sim)
        energies.append(E_total)
        print(f" 半徑 R = {r:.2f} | 勢能 E = {E_total:.3f}")

    # --- 繪圖與分析 ---
    radii = np.array(test_radii)
    energies = np.array(energies)
    
    plt.figure(figsize=(10, 6))
    
    # 畫出測量結果
    plt.plot(radii, energies, 'b.-', markersize=8, linewidth=2, label='Measured Elastic Energy')
    
    # 標示理論上的「網格量子化躍遷點」
    colors = ['r', 'g', 'c', 'm', 'y', 'orange', 'purple', 'brown', 'pink', 'gray']
    for i, d in enumerate(lattice_distances):
        if 0.5 <= d <= 3.2:
            plt.axvline(d, color=colors[i%len(colors)], linestyle='--', alpha=0.7, 
                        label=f'Lattice $\sqrt{{{i+1}}}$ ≈ {d:.2f}')

    plt.xlabel('Topological Defect Radius (R)')
    plt.ylabel('Total Elastic Energy (E)')
    plt.title('Quantum Mass Spectrum in 3D Elastic Lattice')
    
    # 為了看清楚階梯，我們把 Y 軸用對數或適當縮放，這裡先維持線性看真實高度差
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.tight_layout()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    img_filename = f"quantum_mass_spectrum_{timestamp}.png"
    plt.savefig(img_filename, dpi=150)
    print(f"\n🖼️ 質量譜圖表已儲存至: {img_filename}")
    plt.show()

if __name__ == "__main__":
    run_quantum_mass_spectrum()