import cupy as cp
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
from energydot_engine import WaveStringUniverseSim3D

def setup_lens(engine, epsilon=0.75, Rs=6.0):
    """彎曲 alpha 和 gamma 剛度場，模擬重力井（低剛度區）"""
    z, y, x = cp.ogrid[:engine.S, :engine.S, :engine.S]
    r2 = (x - engine.mid)**2 + (y - engine.mid)**2 + (z - engine.mid)**2
    
    lens = 1.0 - epsilon * cp.exp(-r2 / (2.0 * Rs**2))
    engine.alpha_spatial *= lens
    engine.gamma_spatial *= lens
    return lens.get()

def inject_light_packet_traveling(engine, xc, yc, sigma=2.0, amplitude=1.0):
    """注入帶有初始動量、沿 +x 方向行進的高斯光波包"""
    z, y, x = cp.ogrid[:engine.S, :engine.S, :engine.S]
    dx = x - xc
    dy = y - yc
    dz = z - engine.mid
    
    r2 = dx**2 + dy**2 + dz**2
    gaussian = cp.exp(-r2 / (2.0 * sigma**2))
    
    engine.u[1] += amplitude * gaussian
    
    c_approx = cp.sqrt(engine.alpha_base)
    du_dx = -dx / (sigma**2) * gaussian
    engine.v_u[1] += -c_approx * amplitude * du_dx

def track_wave_centroid_2D(field_slice, min_threshold=1e-4):
    """
    💡 加入數值爆炸防護的質心追蹤儀
    """
    max_val = np.max(field_slice)
    
    # 防護一：如果宇宙爆炸 (出現 NaN) 或能量過低，直接回傳 None
    if np.isnan(max_val) or max_val < min_threshold:
        return None, None
        
    mask = field_slice > (max_val * 0.5)
    weights = field_slice[mask]
    
    # 防護二：確保權重總和不為零
    if np.sum(weights) == 0:
        return None, None
        
    y_indices, x_indices = np.indices(field_slice.shape)
    x_cm = np.average(x_indices[mask], weights=weights)
    y_cm = np.average(y_indices[mask], weights=weights)
    
    return x_cm, y_cm

def run_lensing_wavefront():
    print("====================================================")
    print(" 🌌 宇宙引擎 —— 湧現引力透鏡實驗 (質心追蹤版)")
    print("====================================================")

    SIZE = 64
    PML_T = 10
    # 💡 給光子足夠的飛行時間跨越整個宇宙
    STEPS = 6500 
    RECORD_INTERVAL = 50

    EPSILON = 0.8  
    Rs = 5.0       
    IMPACT_PARAM = 5          
    X_SOURCE = PML_T + 2      
    Y_SOURCE = SIZE // 2 + IMPACT_PARAM

    out_dir = "./universe_snapshots_v8_4_0"
    os.makedirs(out_dir, exist_ok=True)

    # ================= 1. 無透鏡參考模擬 (平直時空) =================
    print("\n⚡ 運行無透鏡參考模擬 (平直時空軌跡測量)...")
    ref_eng = WaveStringUniverseSim3D(size=SIZE, pml_thickness=PML_T)
    ref_eng.hbar_noise = 0.0
    inject_light_packet_traveling(ref_eng, xc=X_SOURCE, yc=Y_SOURCE, sigma=2.0, amplitude=0.1)
    
    ref_history = []
    for step in range(STEPS):
        ref_eng.step()
        if step % RECORD_INTERVAL == 0:
            uy_slice = cp.asnumpy(cp.abs(ref_eng.u[1, SIZE//2, :, :]))
            px, py = track_wave_centroid_2D(uy_slice)
            
            if px is not None and X_SOURCE < px < SIZE - PML_T - 2:
                ref_history.append((step, px, py))
                
        if step % 500 == 0 and step > 0:
            print(f"  └─ 進度: Step {step}/{STEPS}")

    # ================= 2. 帶透鏡模擬 (彎曲時空) =================
    print("\n🌌 運行引力透鏡模擬 (彎曲時空軌跡測量)...")
    lens_eng = WaveStringUniverseSim3D(size=SIZE, pml_thickness=PML_T)
    lens_eng.hbar_noise = 0.0
    lens_map = setup_lens(lens_eng, epsilon=EPSILON, Rs=Rs)
    inject_light_packet_traveling(lens_eng, xc=X_SOURCE, yc=Y_SOURCE, sigma=2.0, amplitude=1.0)
    
    lens_history = []
    for step in range(STEPS):
        lens_eng.step()
        if step % RECORD_INTERVAL == 0:
            uy_slice = cp.asnumpy(cp.abs(lens_eng.u[1, SIZE//2, :, :]))
            px, py = track_wave_centroid_2D(uy_slice)
            
            if px is not None and X_SOURCE < px < SIZE - PML_T - 2:
                lens_history.append((step, px, py))
                
        if step % 500 == 0 and step > 0:
            print(f"  └─ 進度: Step {step}/{STEPS}")

    # ================= 3. 數據整合與分析 =================
    df_ref = pd.DataFrame(ref_history, columns=["step", "x_ref", "y_ref"])
    df_lens = pd.DataFrame(lens_history, columns=["step", "x_lens", "y_lens"])
    
    df = pd.merge(df_ref, df_lens, on="step", how="outer").sort_values("step")
    csv_path = os.path.join(out_dir, "lensing_trajectory.csv")
    df.to_csv(csv_path, index=False)
    
    print("\n" + "="*50)
    print(f"💾 [數據歸檔] 軌跡數據已保存：{csv_path}")

    # 計算偏折角
    if not df_lens.empty and not df_ref.empty:
        last_ref = df_ref.dropna().iloc[-1]
        last_lens = df_lens.dropna().iloc[-1]
        delta_y = last_lens['y_lens'] - last_ref['y_ref']
        print(f"📐 測得最終 Y 軸引力偏折量: {delta_y:.4f} 格")
    print("="*50)

    # ================= 4. 繪製精美光跡圖 =================
    plt.style.use('seaborn-v0_8-dark_background' if 'seaborn-v0_8-dark_background' in plt.style.available else 'dark_background')
    fig, ax = plt.subplots(figsize=(9, 8), dpi=150)
    
    im = ax.imshow(lens_map[SIZE//2, :, :], cmap='magma', origin='lower', extent=[0, SIZE, 0, SIZE], alpha=0.85)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Local Stiffness (Speed of Light Modulator)', color='white', fontsize=11)
    
    ax.scatter(SIZE//2, SIZE//2, marker='+', color='cyan', s=200, linewidths=2, label='Gravity Well Center')
    ax.scatter(X_SOURCE, Y_SOURCE, marker='o', color='yellow', s=80, label='Photon Source', zorder=5)

    ax.plot(df["x_ref"], df["y_ref"], color='#00ff00', linestyle='--', linewidth=2.5, alpha=0.8, label='Flat Spacetime')
    ax.plot(df["x_lens"], df["y_lens"], color='#ff4444', linestyle='-', linewidth=3.0, alpha=0.9, label='Lensed Trajectory')
    
    ax.set_title("Emergent Gravitational Lensing in EnergyDot Universe", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("X (Grid)", fontsize=12)
    ax.set_ylabel("Y (Grid)", fontsize=12)
    ax.legend(loc='upper right', framealpha=0.7, fontsize=10)
    
    ax.set_xlim(PML_T, SIZE - PML_T)
    ax.set_ylim(PML_T, SIZE - PML_T)
    ax.grid(True, linestyle=':', alpha=0.3)
    
    png_path = os.path.join(out_dir, "gravitational_lensing_trajectory.png")
    plt.savefig(png_path, bbox_inches='tight', dpi=150)
    plt.close()
    print(f"🎨 [圖表導出] 光跡偏折圖已保存：{png_path}\n")

if __name__ == "__main__":
    run_lensing_wavefront()