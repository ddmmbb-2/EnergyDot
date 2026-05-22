import numpy as np
import matplotlib.pyplot as plt
from energy_dot_lattice_3d_2 import EnergyLatticeSim3D_Relativity

def visualize_curved_spacetime():
    print("🚀 啟動 EnergyDot 數值相對論：計算時空度規 (h_ij)...")
    
    # 啟動相對論引擎
    sim = EnergyLatticeSim3D_Relativity(size=96)
    
    print("   [運算中] 求解愛因斯坦場方程 (靜態真空解) 1000步...")
    for _ in range(1000):
        sim.step()
        
    print("   [完成] 提取應變張量與度規擾動...")
    ux, uy, eps_xx, eps_yy = sim.get_metric_perturbation_2d()
    
    # --- 繪製彎曲時空圖 ---
    S = sim.S
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # 建立平直時空的參考網格座標
    y, x = np.mgrid[0:S, 0:S]
    
    # 圖 1：度規擾動向量場 (時空拖拽)
    # 為了圖表清晰，每隔 4 個網格畫一個箭頭
    skip = (slice(None, None, 4), slice(None, None, 4))
    axes[0].quiver(x[skip], y[skip], ux[skip], uy[skip], color='blue', scale=50)
    axes[0].set_title("Spacetime Displacement Vector Field $\\vec{u}$")
    axes[0].set_aspect('equal')
    axes[0].grid(True, linestyle=':', alpha=0.6)
    
    # 圖 2：彎曲的時空網格 (The Curved Metric)
    # 彎曲後的座標 = 原座標 + 擾動位移 (x + u_x, y + u_y)
    curved_x = x + ux
    curved_y = y + uy
    
    axes[1].set_title("Einstein Curved Metric Space ($g_{\\mu\\nu}$ Grid)")
    # 畫水平網格線
    for i in range(0, S, 4):
        axes[1].plot(curved_x[i, :], curved_y[i, :], 'k-', lw=0.5, alpha=0.5)
    # 畫垂直網格線
    for j in range(0, S, 4):
        axes[1].plot(curved_x[:, j], curved_y[:, j], 'k-', lw=0.5, alpha=0.5)
        
    # 標示質量空洞 (黑洞) 邊界
    circle = plt.Circle((sim.mid, sim.mid), sim.void_R, color='red', fill=False, lw=2, label="Mass Void (Singularity Horizon)")
    axes[1].add_patch(circle)
    
    axes[1].set_aspect('equal')
    axes[1].legend()
    axes[1].set_xlim(sim.mid - 30, sim.mid + 30)
    axes[1].set_ylim(sim.mid - 30, sim.mid + 30)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    visualize_curved_spacetime()