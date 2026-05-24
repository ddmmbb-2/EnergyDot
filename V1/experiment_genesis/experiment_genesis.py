import cupy as cp
import pandas as pd
import time
from energydot_engine import EnergyLatticeSim3D

def run_genesis():
    print("🌌 EnergyDot 創世實驗：從純能量輻射中碰撞出實體物質 (Pair Production)")
    
    # 1. 初始化包含 Skyrme 剛性的真實物理引擎
    size = 96
    sim = EnergyLatticeSim3D(size=size)
    mid = size // 2

    print(">> 在空間兩端注入兩道高能純量波 (光子/輻射)，並賦予相向飛行的動量...")
    z, y, x = cp.ogrid[:size, :size, :size]
    
    # 設定波的寬度與能量 (單一波的能量不足以形成粒子，必須靠相撞疊加)
    width = 4.0
    amp = 3.5  # 注意：3.5 小於 2π，所以它本身不是粒子，只是一道很強的波
    
    # 波 A：位於 Z 軸左側，準備向右飛
    center_A = mid - 15
    r2_A = (x - mid)**2 + (y - mid)**2 + (z - center_A)**2
    wave_A = amp * cp.exp(-r2_A / (2 * width**2))
    
    # 波 B：位於 Z 軸右側，準備向左飛
    center_B = mid + 15
    r2_B = (x - mid)**2 + (y - mid)**2 + (z - center_B)**2
    wave_B = amp * cp.exp(-r2_B / (2 * width**2))
    
    # 將兩道波注入推擠場 u
    sim.u[0] = wave_A + wave_B
    
    # 🌟 賦予動量 (速度) 的關鍵：
    # 為了讓波 A 向右 (+z) 飛，波 B 向左 (-z) 飛，
    # 我們必須在 u_prev 中將它們的波形往反方向稍微偏移，創造出時間演化的速度差！
    shift = 1.0  # 速度偏移量
    r2_A_prev = (x - mid)**2 + (y - mid)**2 + (z - (center_A - shift))**2
    wave_A_prev = amp * cp.exp(-r2_A_prev / (2 * width**2))
    
    r2_B_prev = (x - mid)**2 + (y - mid)**2 + (z - (center_B + shift))**2
    wave_B_prev = amp * cp.exp(-r2_B_prev / (2 * width**2))
    
    sim.u_prev[0] = wave_A_prev + wave_B_prev

    # 2. 開始創世演化
    iterations = 800
    log_interval = 20
    data_log = []

    print(f">> 開始真實時間演化... 觀察波的相撞與拓撲結的湧現")
    start_time = time.time()

    for t in range(iterations):
        sim.step()
        
        if t % log_interval == 0:
            peak_u = float(cp.max(cp.abs(sim.u)))
            vol_u = int(cp.sum(cp.abs(sim.u) > 0.05))
            
            data_log.append({
                'Step': t,
                'Peak_Mass_Amp': round(peak_u, 6),
                'Mass_Volume': vol_u
            })
            
            print(f"Step {t:4d} | 空間最高振幅: {peak_u:.4f} | 影響體積: {vol_u}")

    # 3. 輸出結果
    df = pd.DataFrame(data_log)
    df.to_csv("energydot_genesis.csv", index=False)
    
    elapsed = time.time() - start_time
    print(f"\n✅ 創世實驗完成！耗時 {elapsed:.2f} 秒。")

if __name__ == "__main__":
    run_genesis()