import cupy as cp
import numpy as np
import matplotlib.pyplot as plt
import csv
import time

# ⚡ CUDA 核心 (維持極速波動)
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

def run_scalar_pressure_verification():
    S = 256
    print(f"🚀 初始化 3D 壓力場 (Scalar Pressure Field)，網格大小: {S}^3")
    
    mid_y, mid_z = S // 2, S // 2
    void_R = 15.0
    start_x = 20
    wave_steps = 1000

    # 1. 建立背景壓力場 P(r)
    # 真空背景壓力 P0 = 1.0
    P_bg = cp.ones((S, S, S), dtype=cp.float32)
    
    z, y, x = cp.ogrid[:S, :S, :S]
    dist = cp.sqrt((x - S//2)**2 + (y - S//2)**2 + (z - S//2)**2)
    mask = dist <= void_R

    print("⏳ 正在演化壓力場拉普拉斯 (Laplacian of Pressure)...")
    # 利用熱傳導演化求靜態解 ∇²P = 0
    for _ in range(2000):
        P_lap = (cp.roll(P_bg, 1, 0) + cp.roll(P_bg, -1, 0) +
                 cp.roll(P_bg, 1, 1) + cp.roll(P_bg, -1, 1) +
                 cp.roll(P_bg, 1, 2) + cp.roll(P_bg, -1, 2) - 6 * P_bg)
        P_bg += 0.1 * P_lap
        # 質量空洞是一個「壓力低谷」(拓撲缺陷吸收壓力)
        P_bg[mask] = 0.2  

    print("🌌 從壓力場 1/r 分佈湧現局部波速...")
    # 波速完全由壓力決定：壓力越高，推擠越快；壓力越低，推擠越慢 (引力時間膨脹)
    alpha_base = 0.04
    alpha_curved = alpha_base * P_bg
    alpha_flat = cp.full((S, S, S), alpha_base, dtype=cp.float32)

    impact_y_list = [mid_y + 25, mid_y + 35, mid_y + 45, mid_y + 55, mid_y + 65, mid_y + 75]
    results = []

    print("\n🔦 開始多軌跡掃描實驗...")
    for idx, target_y in enumerate(impact_y_list):
        r_distance = target_y - mid_y
        print(f"   -> 發射第 {idx+1} 道光線 (距離中心 r = {r_distance})...")
        
        flat_final_y = run_single_ray(S, alpha_flat, start_x, target_y, mid_z, wave_steps)
        curved_final_y = run_single_ray(S, alpha_curved, start_x, target_y, mid_z, wave_steps)
        
        net_deflection = flat_final_y - curved_final_y
        results.append({
            'r': r_distance,
            '1_over_r': 1.0 / r_distance,
            'deflection': net_deflection
        })
        print(f"      測得淨偏折量: {net_deflection:.5f}")

    # 📊 繪圖
    r_vals = [res['r'] for res in results]
    inv_r_vals = [res['1_over_r'] for res in results]
    deflections = [res['deflection'] for res in results]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    ax1.plot(r_vals, deflections, 'bo-', linewidth=2, markersize=8)
    ax1.set_title('Deflection vs. Distance ($r$)')
    ax1.set_xlabel('Impact Parameter $r$')
    ax1.set_ylabel('Net Deflection $\Delta y$')
    ax1.grid(True, linestyle='--', alpha=0.6)

    ax2.plot(inv_r_vals, deflections, 'ro-', linewidth=2, markersize=8)
    z_fit = np.polyfit(inv_r_vals, deflections, 1)
    p = np.poly1d(z_fit)
    ax2.plot(inv_r_vals, p(inv_r_vals), "k--", alpha=0.7, label='Linear Fit')
    
    ax2.set_title('Deflection vs. $1/r$ (Strict Potential Test)')
    ax2.set_xlabel('Inverse Distance $1/r$')
    ax2.legend()
    ax2.grid(True, linestyle='--', alpha=0.6)

    plt.suptitle('EnergyDot: Pressure Field ($1/r$) Lensing Verification', fontsize=16)
    plt.tight_layout()
    plt.savefig('scalar_gravity_lens_result.png', dpi=300)
    print("\n✅ 驗證完成！請查看 scalar_gravity_lens_result.png")

if __name__ == "__main__":
    run_scalar_pressure_verification()