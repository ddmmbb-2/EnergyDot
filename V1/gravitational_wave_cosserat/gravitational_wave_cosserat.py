import cupy as cp
import numpy as np
import matplotlib.pyplot as plt
import csv
from PIL import Image
import os
from energydot_engine import EnergyLatticeSim3D

def run_cosserat_gravity_wave():
    print("🚀 [EnergyDot] 啟動 Cosserat 重力波驗證實驗...")
    
    # 初始化宇宙晶格
    size = 120
    sim = EnergyLatticeSim3D(size=size, mode="micro")
    mid = size // 2

    # 實驗設定
    bh_mass = 50.0       # 黑洞拓撲質量
    bh_radius = 4.0      # 鎖定半徑
    distances = [15, 25, 35, 45] # 設置於不同半徑的觀測感測器
    sensor_data = []

    print("🌌 [階段 1] 注入拓撲質量缺陷，建立周圍空間的彈性勢能...")
    sim.inject_black_hole(pos=(mid, mid, mid), mass=bh_mass, charge=0, radius=bh_radius)
    
    # 讓周圍空間適應推擠場 (靜態鎖定)
    for _ in range(30):
        sim.step()

    print("💥 [階段 2] 拓撲湮滅！解除空間鎖定，引發重力波爆發！")
    sim.lock_mask[:] = False
    sim.lock_field_u[:] = 0.0

    # 準備儲存影像
    os.makedirs("frames", exist_ok=True)
    frame_files = []
    total_steps = 150

    # 動態範圍參考值 (用於固定 colormap 讓波紋可見)
    vmax_ke = 0.005 

    for t in range(total_steps):
        sim.step()
        
        # 計算 U 場 (位移場) 的動能密度作為重力波的觀測量
        # E_k = 0.5 * (\partial u / \partial t)^2
        v_u = sim.u - sim.u_prev
        ke_3d = 0.5 * cp.sum(v_u**2, axis=0)
        
        # 記錄感測器數據 (Z軸方向上的波前)
        current_sensors = [t]
        for d in distances:
            val = float(ke_3d[mid, mid, mid + d])
            current_sensors.append(val)
        sensor_data.append(current_sensors)

        # 每 2 步繪製一張 XY 平面切片 (Z = mid)
        if t % 2 == 0:
            ke_slice = cp.asnumpy(ke_3d[mid, :, :]) 
            
            plt.figure(figsize=(6, 5))
            plt.imshow(ke_slice, cmap='magma', origin='lower', vmin=0, vmax=vmax_ke)
            plt.title(f"Cosserat Gravitational Wave | t = {t}")
            plt.colorbar(label='Kinetic Energy Density (u-field)')
            
            # 標示中心震源與感測器位置
            plt.scatter([mid], [mid], c='white', marker='x', label='Source')
            for d in distances:
                plt.scatter([mid+d], [mid], c='cyan', s=12)
            
            filename = f"frames/frame_{t:03d}.png"
            plt.savefig(filename, dpi=100)
            plt.close()
            frame_files.append(filename)
            
            if t % 30 == 0:
                print(f"  -> 演化進度: {t}/{total_steps} 步")

    print("📊 [階段 3] 數據分析與動畫渲染...")
    
    # 1. 寫入 CSV
    csv_filename = "cosserat_gravity_wave_data.csv"
    with open(csv_filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["time_step"] + [f"dist_{d}" for d in distances])
        writer.writerows(sensor_data)
    
    # 2. 製作並儲存 GIF
    gif_filename = "cosserat_gravity_wave.gif"
    images = [Image.open(f) for f in frame_files]
    images[0].save(gif_filename, save_all=True, append_images=images[1:], duration=80, loop=0)
    
    print(f"✅ 實驗完成！已生成動畫 {gif_filename} 以及數據表 {csv_filename}")

if __name__ == "__main__":
    run_cosserat_gravity_wave()