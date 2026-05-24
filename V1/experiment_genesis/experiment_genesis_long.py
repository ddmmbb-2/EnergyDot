import cupy as cp
import pandas as pd
import time
from energydot_engine import EnergyLatticeSim3D

def run_genesis_long():
    print("🌌 EnergyDot 創世實驗：超長時期宇宙冷卻與粒子演化 (20,000 步)")
    
    # 1. 初始化引擎
    size = 96
    sim = EnergyLatticeSim3D(size=size)
    mid = size // 2

    print(">> 注入兩道高能光子波，開始大霹靂碰撞...")
    z, y, x = cp.ogrid[:size, :size, :size]
    
    width = 4.0
    amp = 3.5  # 相撞疊加後會超過 2π
    
    # 波 A 向右飛
    center_A = mid - 15
    r2_A = (x - mid)**2 + (y - mid)**2 + (z - center_A)**2
    wave_A = amp * cp.exp(-r2_A / (2 * width**2))
    
    # 波 B 向左飛
    center_B = mid + 15
    r2_B = (x - mid)**2 + (y - mid)**2 + (z - center_B)**2
    wave_B = amp * cp.exp(-r2_B / (2 * width**2))
    
    sim.u[0] = wave_A + wave_B
    
    # 速度差設定
    shift = 1.0
    r2_A_prev = (x - mid)**2 + (y - mid)**2 + (z - (center_A - shift))**2
    wave_A_prev = amp * cp.exp(-r2_A_prev / (2 * width**2))
    
    r2_B_prev = (x - mid)**2 + (y - mid)**2 + (z - (center_B + shift))**2
    wave_B_prev = amp * cp.exp(-r2_B_prev / (2 * width**2))
    
    sim.u_prev[0] = wave_A_prev + wave_B_prev

    # 2. 🌟 超長時期演化：20,000 步 🌟
    iterations = 20000
    log_interval = 50  # 每 50 步記錄一次，避免 CSV 檔案過大
    data_log = []

    print(f">> 開始漫長的宇宙時間演化... 請耐心等候，這可能需要幾分鐘！")
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
            
            # 每 1000 步印出一次，以免洗版
            if t % 1000 == 0:
                print(f"Step {t:5d} | 空間最高振幅: {peak_u:.4f} | 影響體積: {vol_u}")

    # 3. 輸出結果
    df = pd.DataFrame(data_log)
    csv_name = "energydot_genesis_long.csv"
    df.to_csv(csv_name, index=False)
    
    elapsed = time.time() - start_time
    print(f"\n✅ 超長創世實驗完成！耗時 {elapsed:.2f} 秒。")
    print(f"💾 數據已儲存至：{csv_name}")

if __name__ == "__main__":
    run_genesis_long()