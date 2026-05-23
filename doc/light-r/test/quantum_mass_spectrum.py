import cupy as cp
import numpy as np
import matplotlib.pyplot as plt
import csv
from datetime import datetime
from lattice_core import EnergyLatticeSim3D

def compute_micropolar_potential_energy(sim):
    """精確計算空間形變勢能 (包含 u 與 theta 場)"""
    pot = cp.zeros((sim.S, sim.S, sim.S), dtype=cp.float32)
    for i in range(3):
        # U 勢能
        gu_x = (cp.roll(sim.u[i], -1, axis=2) - cp.roll(sim.u[i], 1, axis=2)) / 2.0
        gu_y = (cp.roll(sim.u[i], -1, axis=1) - cp.roll(sim.u[i], 1, axis=1)) / 2.0
        gu_z = (cp.roll(sim.u[i], -1, axis=0) - cp.roll(sim.u[i], 1, axis=0)) / 2.0
        pot += 0.5 * sim.alpha * (gu_x**2 + gu_y**2 + gu_z**2)
        
        # Theta 勢能
        gt_x = (cp.roll(sim.theta[i], -1, axis=2) - cp.roll(sim.theta[i], 1, axis=2)) / 2.0
        gt_y = (cp.roll(sim.theta[i], -1, axis=1) - cp.roll(sim.theta[i], 1, axis=1)) / 2.0
        gt_z = (cp.roll(sim.theta[i], -1, axis=0) - cp.roll(sim.theta[i], 1, axis=0)) / 2.0
        pot += 0.5 * sim.gamma * (gt_x**2 + gt_y**2 + gt_z**2)
        
    valid_mask = cp.ones_like(pot, dtype=bool)
    margin = 10
    valid_mask[:margin, :, :] = False
    valid_mask[-margin:, :, :] = False
    valid_mask[:, :margin, :] = False
    valid_mask[:, -margin:, :] = False
    valid_mask[:, :, :margin] = False
    valid_mask[:, :, -margin:] = False
    
    valid_mask = valid_mask & (~sim.lock_mask[0])
    return float(cp.sum(pot[valid_mask]))

def run_quantum_mass_spectrum():
    print("⚛️ 啟動 EnergyDot 微極晶格：粒子的量子質量譜掃描 (大一統版)")
    
    test_radii = np.arange(0.5, 3.25, 0.05)
    energies = []
    lattice_distances = [np.sqrt(i) for i in range(1, 11)]
    
    for r in test_radii:
        sim = EnergyLatticeSim3D(size=64, mode="micro")
        mass = r * 10.0 
        # 注入無自旋的純質量缺陷
        sim.inject_black_hole((sim.mid, sim.mid, sim.mid), mass=mass, charge=0.0, radius=r)
        
        for _ in range(150):
            sim.step()
            
        E_total = compute_micropolar_potential_energy(sim)
        energies.append(E_total)
        print(f" 半徑 R = {r:.2f} | 總勢能 E = {E_total:.3f}")

    radii = np.array(test_radii)
    energies = np.array(energies)
    
    plt.figure(figsize=(10, 6))
    plt.plot(radii, energies, 'b.-', markersize=8, linewidth=2, label='Micropolar Elastic Energy')
    
    colors = ['r', 'g', 'c', 'm', 'y', 'orange', 'purple', 'brown', 'pink', 'gray']
    for i, d in enumerate(lattice_distances):
        if 0.5 <= d <= 3.2:
            plt.axvline(d, color=colors[i%len(colors)], linestyle='--', alpha=0.7, 
                        label=f'Lattice $\sqrt{{{i+1}}}$ ≈ {d:.2f}')

    plt.xlabel('Topological Defect Radius (R)')
    plt.ylabel('Total Elastic Energy (E)')
    plt.title('Quantum Mass Spectrum in Unified Micropolar Lattice')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.tight_layout()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    img_filename = f"quantum_mass_spectrum_v2_{timestamp}.png"
    plt.savefig(img_filename, dpi=150)
    print(f"\n🖼️ 圖表已儲存至: {img_filename}")
    plt.show()

if __name__ == "__main__":
    run_quantum_mass_spectrum()