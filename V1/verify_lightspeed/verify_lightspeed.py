import cupy as cp
import numpy as np
import matplotlib.pyplot as plt
import imageio.v2 as imageio
import csv
import os
from scipy.stats import linregress
from energydot_engine import EnergyLatticeSim3D

def run_lightspeed_experiment(steps=80, size=96, threshold=1e-4):
    print("🌌 EnergyDot 第一性原理：啟動「光速極限」驗證實驗...")
    
    # 建立輸出資料夾
    output_dir = "lightspeed_results"
    os.makedirs(output_dir, exist_ok=True)
    csv_filename = os.path.join(output_dir, "light_speed_data.csv")
    gif_filename = os.path.join(output_dir, "light_propagation.gif")
    png_filenames = []
    
    # 1. 啟動模擬引擎
    sim = EnergyLatticeSim3D(size=size, mode="micro")
    theoretical_c = np.sqrt(sim.gamma)
    print(f"📐 引擎參數 gamma = {sim.gamma}")
    print(f"📐 理論光波速 limit (c) = {theoretical_c:.4f} grid/step")
    
    # 2. 注入光子脈衝 (在中心產生一個高斯分佈的自旋扭轉波)
    z, y, x = cp.ogrid[:sim.S, :sim.S, :sim.S]
    r2 = (x - sim.mid)**2 + (y - sim.mid)**2 + (z - sim.mid)**2
    pulse_radius = 1.5
    
    # 激發 Z 軸自旋 (產生純橫波輻射)
    sim.theta[0] += cp.exp(-r2 / (2 * pulse_radius**2))
    sim.theta_prev = cp.zeros_like(sim.theta) # 確保有初始擴散動能
    
    # 預先計算每個格點到中心的距離陣列 (用於找波前)
    distances = cp.sqrt(r2)
    
    data_log = []
    prev_max_dist = 0.0
    
    # 3. 開始演化與記錄
    print("\n🚀 開始演化...")
    for step in range(steps):
        sim.step()
        
        # 計算 theta 場的總向量振幅 ||θ||
        theta_amp = cp.sqrt(sim.theta[0]**2 + sim.theta[1]**2 + sim.theta[2]**2)
        
        # 尋找大於閾值的最遠半徑 (波前)
        mask = theta_amp > threshold
        if cp.any(mask):
            max_dist = cp.max(distances[mask]).item()
        else:
            max_dist = 0.0
            
        # 計算瞬時速度
        instant_speed = max_dist - prev_max_dist if step > 0 else 0.0
        prev_max_dist = max_dist
        
        data_log.append([step, max_dist, instant_speed, theoretical_c])
        
        # --- 視覺化 2D 切面 (Z = mid) ---
        slice_2d = theta_amp[sim.mid, :, :].get()
        
        fig, ax = plt.subplots(figsize=(6, 6))
        # 使用 log scale 或限制 vmax 來凸顯微弱的波前
        cax = ax.imshow(slice_2d, cmap='magma', vmin=0, vmax=0.05, origin='lower')
        ax.set_title(f"Step {step:03d} | Radius: {max_dist:.2f} | Speed: {instant_speed:.4f}")
        
        # 畫出理論光錐的藍色虛線圓圈
        theory_radius = step * theoretical_c + pulse_radius
        circle = plt.Circle((sim.mid, sim.mid), theory_radius, 
                            color='cyan', fill=False, linestyle='--', linewidth=1.5, label='Theory Light Cone')
        ax.add_patch(circle)
        ax.legend(loc="upper right", framealpha=0.7)
        ax.axis('off')
        
        filename = os.path.join(output_dir, f"frame_{step:03d}.png")
        plt.savefig(filename, dpi=100, bbox_inches='tight', facecolor='black')
        plt.close(fig)
        png_filenames.append(filename)
        
        if step % 10 == 0:
            print(f"⏳ Step {step:03d}/{steps} | 波前距離: {max_dist:.2f} | 瞬時速度: {instant_speed:.4f}")

    # 4. 輸出 CSV
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Step", "Wavefront_Radius", "Instant_Speed", "Theoretical_Speed"])
        writer.writerows(data_log)
    print(f"\n📊 數據已儲存至: {csv_filename}")

    # 5. 生成 GIF 動畫
    print(f"🎬 正在合成 GIF 動畫...")
    with imageio.get_writer(gif_filename, mode='I', duration=0.08) as writer:
        for filename in png_filenames:
            image = imageio.imread(filename)
            writer.append_data(image)
            # 可選：刪除暫存的 PNG 檔案以節省空間
            # os.remove(filename) 
    print(f"✅ 動畫已生成: {gif_filename}")
    
    # 6. 計算實驗總結 (使用線性迴歸計算平均波速)
    steps_array = np.array([row[0] for row in data_log[10:]])  # 排除前 10 步啟動非線性期
    radius_array = np.array([row[1] for row in data_log[10:]])
    
    if len(steps_array) > 1:
        slope, intercept, r_value, p_value, std_err = linregress(steps_array, radius_array)
        measured_c = slope
        error_rate = abs(measured_c - theoretical_c) / theoretical_c * 100
        
        print(f"\n🏆 實驗結果總結 (基於線性迴歸):")
        print(f"  👉 理論光速 (c): {theoretical_c:.4f} grid/step")
        print(f"  👉 實測波速 (v): {measured_c:.4f} grid/step (R² = {r_value**2:.4f})")
        print(f"  👉 相對誤差率 : {error_rate:.2f}%")
        
        if error_rate > 5.0:
            print("  ⚠️ 注意：誤差略大。這可能是因為 kappa 齒輪耦合項造成的色散，或是邊界效應所致。")
        else:
            print("  🎉 驗證成功！波動嚴格遵守第一性原理的介質極限。")

if __name__ == "__main__":
    # 執行實驗，預設跑 70 步，在 96x96x96 的空間中
    run_lightspeed_experiment(steps=70, size=96)