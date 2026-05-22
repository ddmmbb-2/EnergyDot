import cupy as cp
import numpy as np
import matplotlib.pyplot as plt
import csv

# ⚡ CUDA 核心 (完全不變)
wave_kernel = cp.RawKernel(r'''
extern "C" __global__
void update_wave(const float* u, const float* u_prev, const float* alpha, float* u_next, int S) {
    int x = blockIdx.x * blockDim.x + threadIdx.x;
    int y = blockIdx.y * blockDim.y + threadIdx.y;
    int z = blockIdx.z * blockDim.z + threadIdx.z;

    if (x > 0 && x < S - 1 && y > 0 && y < S - 1 && z > 0 && z < S - 1) {
        int idx = z * S * S + y * S + x;
        float laplacian = u[idx - 1] + u[idx + 1] + 
                          u[idx - S] + u[idx + S] + 
                          u[idx - S*S] + u[idx + S*S] - 
                          6.0 * u[idx];

        float next_val = 2.0 * u[idx] - u_prev[idx] + alpha[idx] * laplacian;

        if (x < 15 || x >= S - 15 || y < 15 || y >= S - 15 || z < 15 || z >= S - 15) {
            next_val *= 0.9; 
        }
        u_next[idx] = next_val;
    }
}
''', 'update_wave')

def run_single_ray(S, alpha_local, start_x, impact_y, mid_z, steps):
    u_wave = cp.zeros((S, S, S), dtype=cp.float32)
    u_wave_prev = cp.zeros((S, S, S), dtype=cp.float32)
    u_wave_next = cp.zeros((S, S, S), dtype=cp.float32)
    
    z, y, x = cp.ogrid[:S, :S, :S]
    packet_radius = 5.0
    
    u_wave = cp.exp(-((x - start_x)**2 + (y - impact_y)**2 + (z - mid_z)**2) / (2 * packet_radius**2)).astype(cp.float32)
    u_wave_prev = cp.exp(-((x - (start_x - 1))**2 + (y - impact_y)**2 + (z - mid_z)**2) / (2 * packet_radius**2)).astype(cp.float32)

    block_size = 8
    grid_size = (S + block_size - 1) // block_size
    blocks = (grid_size, grid_size, grid_size)
    threads = (block_size, block_size, block_size)

    final_y = impact_y
    for t in range(steps):
        wave_kernel(blocks, threads, (u_wave, u_wave_prev, alpha_local, u_wave_next, S))
        u_wave_prev, u_wave, u_wave_next = u_wave, u_wave_next, u_wave_prev
        
        if t == steps - 1:
            energy = u_wave**2
            total_energy = cp.sum(energy)
            if total_energy > 1e-5 and not cp.isnan(total_energy): 
                final_y = float(cp.sum(y * energy) / total_energy)
    return final_y

def run_einstein_verification():
    S = 256
    print(f"🚀 初始化 3D 壓力場 (Scalar Pressure Field)，網格大小: {S}^3")
    
    mid_y, mid_z = S // 2, S // 2
    void_R = 15.0
    start_x = 20
    wave_steps = 1000

    # 1. 建立背景壓力場 P(r)
    P_bg = cp.ones((S, S, S), dtype=cp.float32)
    z, y, x = cp.ogrid[:S, :S, :S]
    dist = cp.sqrt((x - S//2)**2 + (y - S//2)**2 + (z - S//2)**2)
    mask = dist <= void_R

    print("⏳ 正在演化壓力場拉普拉斯 (Laplacian of Pressure)...")
    for _ in range(2000):
        P_lap = (cp.roll(P_bg, 1, 0) + cp.roll(P_bg, -1, 0) +
                 cp.roll(P_bg, 1, 1) + cp.roll(P_bg, -1, 1) +
                 cp.roll(P_bg, 1, 2) + cp.roll(P_bg, -1, 2) - 6 * P_bg)
        P_bg += 0.1 * P_lap
        P_bg[mask] = 0.2  

    print("🌌 從壓力場湧現局部波速 (牛頓 vs 愛因斯坦)...")
    alpha_base = 0.04
    alpha_flat = cp.full((S, S, S), alpha_base, dtype=cp.float32)
    
    # 🍎 牛頓極限：僅考慮時間膨脹 (壓力一階耦合)
    alpha_newton = alpha_base * P_bg
    
    # 🌟 愛因斯坦極限：時間膨脹 + 空間幾何拉長 (壓力平方耦合)
    alpha_einstein = alpha_base * (P_bg ** 2)

    impact_y_list = [mid_y + 25, mid_y + 35, mid_y + 45, mid_y + 55, mid_y + 65, mid_y + 75]
    results = []

    print("\n🔦 開始三軌跡並行掃描實驗 (平直 vs 牛頓 vs 愛因斯坦)...")
    for idx, target_y in enumerate(impact_y_list):
        r_distance = target_y - mid_y
        print(f"   -> 發射第 {idx+1} 道光線 (距離中心 r = {r_distance})...")
        
        flat_y = run_single_ray(S, alpha_flat, start_x, target_y, mid_z, wave_steps)
        newton_y = run_single_ray(S, alpha_newton, start_x, target_y, mid_z, wave_steps)
        einstein_y = run_single_ray(S, alpha_einstein, start_x, target_y, mid_z, wave_steps)
        
        deflection_newton = flat_y - newton_y
        deflection_einstein = flat_y - einstein_y
        
        results.append({
            'r': r_distance,
            '1_over_r': 1.0 / r_distance,
            'deflection_newton': deflection_newton,
            'deflection_einstein': deflection_einstein,
            'ratio': deflection_einstein / deflection_newton if deflection_newton != 0 else 0
        })
        print(f"      🍏 牛頓偏折: {deflection_newton:.5f} | 🪐 愛因斯坦偏折: {deflection_einstein:.5f} | 倍率: {results[-1]['ratio']: .2f}x")

    # 📊 繪圖比較
    inv_r_vals = [res['1_over_r'] for res in results]
    defl_n = [res['deflection_newton'] for res in results]
    defl_e = [res['deflection_einstein'] for res in results]

    plt.figure(figsize=(10, 8))
    
    # 繪製愛因斯坦線
    plt.plot(inv_r_vals, defl_e, 'ro', markersize=8, label='Einstein (Time + Space Warp)')
    z_e = np.polyfit(inv_r_vals, defl_e, 1)
    p_e = np.poly1d(z_e)
    plt.plot(inv_r_vals, p_e(inv_r_vals), "r-", linewidth=2)

    # 繪製牛頓線
    plt.plot(inv_r_vals, defl_n, 'bo', markersize=8, label='Newton (Time Dilation Only)')
    z_n = np.polyfit(inv_r_vals, defl_n, 1)
    p_n = np.poly1d(z_n)
    plt.plot(inv_r_vals, p_n(inv_r_vals), "b--", linewidth=2)
    
    plt.title('EnergyDot: 1919 Solar Eclipse Simulation\nNewton vs. Einstein Deflection ($1/r$)', fontsize=15)
    plt.xlabel('Inverse Distance $1/r$', fontsize=12)
    plt.ylabel('Net Deflection $\Delta y$', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)

    # 在圖表上加上倍率文字
    ratio_avg = np.mean([res['ratio'] for res in results])
    plt.text(min(inv_r_vals), max(defl_e)*0.9, f"Average Deflection Ratio (Einstein / Newton) ≈ {ratio_avg:.2f}x", 
             fontsize=12, bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))

    plt.tight_layout()
    plt.savefig('einstein_gravity_lens_result.png', dpi=300)
    print("\n✅ 愛因斯坦驗證完成！請查看 einstein_gravity_lens_result.png")

if __name__ == "__main__":
    run_einstein_verification()