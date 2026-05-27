import cupy as cp
import numpy as np
import matplotlib.pyplot as plt

def run_perfect_cfl_test(max_steps=5500): # 💡 修正 1：擴大總步數，讓波包有足夠時間跑到 32 格外
    from energydot_engine import WaveStringUniverseSim3D
    
    sim = WaveStringUniverseSim3D(size=128, pml_thickness=16)
    sim.hbar_noise = 0.0  # 保持純淨決定論幾何傳播
    
    mid = sim.mid
    dt = sim.dt
    
    # 注入乾淨的局域微擾
    z, y, x = cp.ogrid[:sim.S, :sim.S, :sim.S]
    dist_sq = (x - mid)**2 + (y - mid)**2 + (z - mid)**2
    pulse = 1.0 * cp.exp(-dist_sq / (2.0 * (1.0**2))) 
    
    sim.u[0] = pulse 
    
    # 探針腹地維持 12 格與 32 格
    dist_A = 12   # 網格 76
    dist_B = 32   # 網格 96
    
    timesteps = []
    sig_A = []
    sig_B = []
    
    print("🚀 完美波前閾值示波器啟動（時空大尺度步數演化中...）")
    for step in range(1, max_steps):
        sim.step()
        
        # 每 5 步記錄一次，大幅優化記憶體並加快運行速度
        if step % 5 == 0:
            t = step * dt
            timesteps.append(t)
            
            # 讀取平移場速度平方（動能密度）
            energy_density = cp.sum(sim.v_u**2, axis=0)
            
            sig_A.append(float(energy_density[mid, mid, mid + dist_A]))
            sig_B.append(float(energy_density[mid, mid, mid + dist_B]))

    return np.array(timesteps), np.array(sig_A), np.array(sig_B), dist_A, dist_B, sim.alpha_base

if __name__ == "__main__":
    times, sig_A, sig_B, d_A, d_B, alpha_base = run_perfect_cfl_test()
    
    # 引入防崩潰的閾值查找機制
    threshold_A = max(sig_A) * 0.01
    threshold_B = max(sig_B) * 0.01
    
    indices_A = np.where(sig_A > threshold_A)[0]
    indices_B = np.where(sig_B > threshold_B)[0]
    
    # 💡 修正 2：如果閾值法安全抓到就用閾值，若沒抓到則自動降級使用最大值，雙重保險不崩潰
    if len(indices_A) > 0 and len(indices_B) > 0:
        idx_start_A = indices_A[0]
        idx_start_B = indices_B[0]
        print("💡 成功啟用 [物理波前閾值法] 計時")
    else:
        idx_start_A = np.argmax(sig_A)
        idx_start_B = np.argmax(sig_B)
        print("💡 閾值未觸發，自動切換至 [全域波峰最大值法] 計時")
    
    t_A = times[idx_start_A]
    t_B = times[idx_start_B]
    
    delta_t = t_B - t_A
    delta_d = d_B - d_A
    
    c_measured = delta_d / delta_t if delta_t > 0 else 0
    c_theoretical = np.sqrt(alpha_base) 
    error_pct = abs(c_measured - c_theoretical) / c_theoretical * 100
    
    print("\n" + "="*50)
    print(f"探針 A 計時時間點: {t_A:.4f} (索引: {idx_start_A})")
    print(f"探針 B 計時時間點: {t_B:.4f} (索引: {idx_start_B})")
    print(f"距離差 Δd = {delta_d} 格, 時間差 Δt = {delta_t:.4f}")
    print("-"*50)
    print(f"實測光速 c_measured    = {c_measured:.6f}")
    print(f"理論光速 c_theoretical = {c_theoretical:.6f}")
    print(f"網格色散數值誤差       = {error_pct:.4f}%")
    print("="*50)
    
    plt.figure(figsize=(7, 4), dpi=100)
    plt.plot(times, sig_A, label=f'Probe A (+{d_A})')
    plt.plot(times, sig_B, label=f'Probe B (+{d_B})')
    plt.axvline(x=t_A, color='blue', linestyle='--')
    plt.axvline(x=t_B, color='green', linestyle='--')
    plt.title(f"Wavefront Mode: Measured c = {c_measured:.4f}")
    plt.xlabel("Time (t)")
    plt.ylabel("Energy Density")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig("./fast_oscilloscope_curve.png")
    print("📊 完美波動追蹤圖形已重新覆蓋存檔。")