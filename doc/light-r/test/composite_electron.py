import cupy as cp
import numpy as np
import matplotlib.pyplot as plt
from lattice_core import EnergyLatticeSim3D

def run_electron_simulation():
    print("⚡ 啟動 EnergyDot 微極晶格：複合粒子 (電子) 生成實驗")
    
    # 建立宇宙 (為了畫圖清晰，尺寸稍微小一點)
    grid_size = 60
    sim = EnergyLatticeSim3D(size=grid_size, mode="micro")
    mid = sim.mid
    
    # --- 粒子的內稟屬性 ---
    R_electron = 2.0       # 極微小的拓撲半徑
    Mass = 5.0             # 質量 (向外的微弱排擠)
    Charge = -15.0         # 負電荷 (強烈的向內拉扯散度)
    Spin_Z = 20.0          # 1/2 自旋 (強烈的 Z 軸原地扭轉)
    
    # 計算複合向心推擠力 (引力 + 靜電力)
    effective_radial_force = Mass + Charge 
    
    print(f"▶ 注入幾何特徵:")
    print(f"  - 半徑: {R_electron}")
    print(f"  - 徑向場 (質量+電荷): {effective_radial_force}")
    print(f"  - 渦旋場 (自旋 Z): {Spin_Z}")
    
    # 利用我們寫好的大一統注入器 (自帶 spin_vector 參數)
    sim.inject_black_hole(
        pos=(mid, mid, mid), 
        mass=effective_radial_force, 
        charge=0.0, # 我們已經將電荷合併到 mass 參數中表現為徑向力
        radius=R_electron, 
        spin_vector=(0.0, 0.0, Spin_Z)
    )
    
    # 演化 100 步，讓電子的形變場向外擴散並達到靜態平衡
    print("  等待空間幾何穩定 (100步)...", end="", flush=True)
    for _ in range(100):
        sim.step()
    print(" 完成！")

    # --- 視覺化觀測：切出 XY 平面 (Z = mid) 的空間推擠場 u ---
    # sim.u 的形狀是 (3, Z, Y, X)，我們取 Z = mid 的切片
    u_np = cp.asnumpy(sim.u)
    
    # 取得 XY 平面上的 Y 分量與 X 分量 (注意陣列索引：u[1] 是 Y, u[2] 是 X)
    u_y = u_np[1, mid, :, :]
    u_x = u_np[2, mid, :, :]
    
    # 建立網格座標用於繪圖
    Y, X = np.mgrid[0:grid_size, 0:grid_size]
    
    # 計算位移場的大小 (用於背景顏色)
    u_mag = np.sqrt(u_x**2 + u_y**2)
    
    # --- 繪圖 ---
    plt.figure(figsize=(10, 8))
    
    # 畫出能量密度/位移強度的熱力圖
    # 使用對數尺度來凸顯微弱的遠場效應
    plt.pcolormesh(X, Y, np.log1p(u_mag), shading='auto', cmap='magma')
    plt.colorbar(label='Log(Displacement Magnitude)')
    
    # 畫出向量場 (Quiver) - 每隔 2 格畫一個箭頭避免太密
    step = 2
    plt.quiver(X[::step, ::step], Y[::step, ::step], 
               u_x[::step, ::step], u_y[::step, ::step], 
               color='cyan', pivot='mid', scale_units='xy', alpha=0.8)
    
    # 標示電子核心
    circle = plt.Circle((mid, mid), R_electron, color='white', fill=False, linestyle='--', linewidth=2)
    plt.gca().add_patch(circle)
    
    plt.title('Geometry of an Electron in EnergyDot Universe\n(Coupled Radial & Spin Fields)', color='white')
    plt.xlabel('X grid')
    plt.ylabel('Y grid')
    
    # 設定深色背景模式
    plt.gca().set_facecolor('black')
    fig = plt.gcf()
    fig.patch.set_facecolor('black')
    plt.gca().tick_params(colors='white')
    plt.gca().xaxis.label.set_color('white')
    plt.gca().yaxis.label.set_color('white')
    
    plt.tight_layout()
    plt.savefig('composite_electron_geometry.png', facecolor=fig.get_facecolor(), edgecolor='none', dpi=150)
    print("🖼️ 電子幾何結構圖已儲存至: composite_electron_geometry.png")
    plt.show()

if __name__ == "__main__":
    run_electron_simulation()