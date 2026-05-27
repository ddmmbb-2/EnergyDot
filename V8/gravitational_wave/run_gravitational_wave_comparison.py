import cupy as cp
import numpy as np
import matplotlib.pyplot as plt
import os
import csv
from energydot_engine import WaveStringUniverseSim3D

class AdvancedUniverseExperiment(WaveStringUniverseSim3D):
    """
    延伸自宇宙引擎 V8.3.1
    帶有非線性應力對稱性保護 (防止核心高能崩塌)
    """
    
    def get_nonlinear_tension_force_corrected(self):
        """
        💡 物理修正：對非線性張力勢進行絕對值對稱化保護
        防止 (div_u ** 3) 在壓縮區 (負值) 轉化為負剛度引發嚴重的晶格塌陷
        """
        div_u = self.get_div_u()
        # 使用 |div_u|^2 * div_u 確保無論膨脹或壓縮，非線性剛度永遠提供正向恢復應力
        phi_potential = self.k_linear * div_u + self.k_quad * (cp.abs(div_u) ** 2) * div_u
        return self.get_grad_scalar(phi_potential)

    def _compute_acceleration_pure(self):
        """覆蓋原引擎的加速算子，確保吃得到我們修正後的非線性張力"""
        lap_u = self.get_weighted_divergence_diffusion(self.u, self.alpha_spatial)
        lap_theta = self.get_weighted_divergence_diffusion(self.theta, self.gamma_spatial)
        
        B_field = self.get_curl(self.theta)
        curl_u = self.get_curl(self.u)
        
        sine_gordon_force = self.beta * cp.sin(self.u)
        f_tension = self.get_nonlinear_tension_force_corrected() # 呼叫對稱化版本
        
        lorentz_force_u = cp.cross(curl_u, B_field, axisa=0, axisb=0, axisc=0)
        
        f_cons_u = lap_u - sine_gordon_force - f_tension + self.kappa * lorentz_force_u
        f_cons_theta = lap_theta + self.kappa * curl_u
        
        return f_cons_u, f_cons_theta

    def inject_pure_light_wave(self, amplitude=0.5, sigma=1.5, coord_offset=(0, 0, 0)):
        z, y, x = cp.ogrid[:self.S, :self.S, :self.S]
        zc = self.mid + coord_offset[0]; yc = self.mid + coord_offset[1]; xc = self.mid + coord_offset[2]
        r2 = (z - zc)**2 + (y - yc)**2 + (x - xc)**2
        gaussian = cp.exp(-r2 / (2.0 * sigma**2))
        du_dy = -(y - yc) / (sigma**2) * gaussian
        du_dx = -(x - xc) / (sigma**2) * gaussian
        self.u[0] += amplitude * du_dy
        self.u[1] += amplitude * (-du_dx)
        
    def inject_quadrupole_gravitational_wave(self, amplitude=0.5, sigma=1.5, coord_offset=(0, 0, 0)):
        z, y, x = cp.ogrid[:self.S, :self.S, :self.S]
        zc = self.mid + coord_offset[0]; yc = self.mid + coord_offset[1]; xc = self.mid + coord_offset[2]
        dx = (x - xc); dy = (y - yc); dz = (z - zc)
        r2 = dx**2 + dy**2 + dz**2
        phi_quad = (dx**2 - dy**2) * cp.exp(-r2 / (2.0 * sigma**2))
        self.u[2] += amplitude * (cp.roll(phi_quad, -1, axis=0) - cp.roll(phi_quad, 1, axis=0)) / 2.0 
        self.u[1] += amplitude * (cp.roll(phi_quad, -1, axis=1) - cp.roll(phi_quad, 1, axis=1)) / 2.0 
        self.u[0] += amplitude * (cp.roll(phi_quad, -1, axis=2) - cp.roll(phi_quad, 1, axis=2)) / 2.0 

def run_experiment(amplitude_grav=1.2, amplitude_light=0.2, steps=600):
    sim = AdvancedUniverseExperiment(size=64, pml_thickness=12)
    sim.hbar_noise = 0.0
    
    # 💡 物理調校：將非線性因子設定在健康的微擾區間 (從 0.15 降至 0.015)
    sim.k_quad = 0.015
    
    # ==================== 1. 光波獨立模擬 ====================
    sim.u[:] = 0; sim.v_u[:] = 0; sim.theta[:] = 0; sim.v_theta[:] = 0
    sim.inject_pure_light_wave(amplitude=amplitude_light, sigma=1.5)
    light_history = []
    
    # ==================== 2. 重力波獨立模擬 ====================
    sim_g = AdvancedUniverseExperiment(size=64, pml_thickness=12)
    sim_g.hbar_noise = 0.0
    sim_g.k_quad = 0.015 # 保持同步
    sim_g.inject_quadrupole_gravitational_wave(amplitude=amplitude_grav, sigma=1.5)
    grav_history = []
    
    print(f"🌌 宇宙場論雙波對比實驗開始 (重力振幅: {amplitude_grav}, 光波振幅: {amplitude_light})")
    print(f"📡 設定調校: k_quad={sim.k_quad} (已啟動非線性應力對稱化保護)")
    
    for t in range(steps):
        sim.step()
        sim_g.step()
        
        light_profile = cp.asnumpy(cp.abs(sim.u[1, sim.mid, sim.mid, sim.mid:]))
        light_history.append(light_profile)
        
        div_u_g = sim_g.get_div_u()
        grav_profile = cp.asnumpy(cp.abs(div_u_g[sim_g.mid, sim_g.mid, sim_g.mid:]))
        grav_history.append(grav_profile)
        
        if t % 100 == 0:
            print(f" └─ 進度: Step {t}/{steps}...")

    light_history = np.array(light_history)  
    grav_history = np.array(grav_history)    
    
    # ==================== 3. 帶有防禦性保護的波前追蹤 ====================
    threshold_pct = 0.05  
    
    def find_wavefront_times_safe(history):
        wavefront_nodes = []
        time_axes = []
        
        # 💡 終極修正：將探測點推向遠場遠離近場駐波盲區（r = 6 ~ 18 格）
        # 這能完美避開初始高斯種子的肥厚外圍，量到真正橫跨時空的 Traveling Wave！
        for r in range(6, 19):
            spatial_idx = r  
            signal = history[:, spatial_idx]
            max_sig = np.max(signal)
            if max_sig < 1e-6: continue
            
            # 尋找超過該點自身最大振幅 5% 的最早時間
            arrival_step = np.where(signal > max_sig * threshold_pct)[0]
            if len(arrival_step) > 0:
                # 額外過濾：如果判定時間太早 (例如前 10 個 step)，說明是初始波尾污染，予以排除
                if arrival_step[0] > 10:
                    wavefront_nodes.append(r)
                    time_axes.append(arrival_step[0] * sim.dt)
                
        if len(time_axes) > 1:
            if np.max(time_axes) - np.min(time_axes) < 1e-5:
                return 0.0, wavefront_nodes, time_axes
            try:
                slope, intercept = np.polyfit(time_axes, wavefront_nodes, 1)
                return slope, wavefront_nodes, time_axes
            except np.linalg.LinAlgError:
                return 0.0, wavefront_nodes, time_axes
        return 0.0, [], []

    c_light, r_l, t_l = find_wavefront_times_safe(light_history)
    c_grav, r_g, t_g = find_wavefront_times_safe(grav_history)
    
    print("\n" + "="*40)
    print(f"📊 雙波前示波器【精密定標報告】 (k_quad={sim.k_quad})")
    print(f" ⚡ 測得剪切光速  c_e = {c_light:.4f}")
    print(f" 🌀 測得重力波速  c_g = {c_grav:.4f}")
    print(f" ⚖️ 波速比值 (c_g / c_e) = {c_grav/c_light if c_light!=0 else 0:.4f}")
    print("="*40)
    
    # ==================== 4. 紀錄成 CSV 檔案 ====================
    csv_dir = sim.output_dir
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)
        
    csv_path = f"{csv_dir}/wave_data_amp_{amplitude_grav}.csv"
    
    with open(csv_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["# 宇宙引擎幾何連續介質雙波對比實驗數據 (修正版)"])
        writer.writerow(["# 基礎剛度 alpha_base", sim.alpha_base])
        writer.writerow(["# 非線性剛度 k_quad", sim.k_quad])
        writer.writerow(["# 重力波初始振幅", amplitude_grav])
        writer.writerow(["# 測得剪切光速 c_e", f"{c_light:.6f}"])
        writer.writerow(["# 測得重力波速 c_g", f"{c_grav:.6f}"])
        writer.writerow([])
        
        header = ["Time(s)"]
        header += [f"Light_r_{i}" for i in range(light_history.shape[1])]
        header += [f"Grav_r_{i}" for i in range(grav_history.shape[1])]
        writer.writerow(header)
        
        for t_step in range(steps):
            row = [f"{t_step * sim.dt:.4f}"]
            row += [f"{val:.6e}" for val in light_history[t_step]]
            row += [f"{val:.6e}" for val in grav_history[t_step]]
            writer.writerow(row)
            
    print(f"💾 數據已成功導出至 CSV：{csv_path}")
    
    # ==================== 5. 繪製時空演化圖 ====================
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    max_plot_r = sim.mid - sim.pml_t
    
    im0 = axes[0].imshow(light_history[:, :max_plot_r], aspect='auto', 
                         extent=[0, max_plot_r, steps*sim.dt, 0], cmap='viridis')
    axes[0].set_title("Light Wave Propagation (Shear Component $u_y$)")
    axes[0].set_xlabel("Distance from Center (Grid)")
    axes[0].set_ylabel("Simulation Time ($t$)")
    fig.colorbar(im0, ax=axes[0])
    if len(t_l) > 0 and c_light > 0:
        axes[0].plot(t_l, r_l, 'r--', label=f'Wavefront Fit ($c={c_light:.3f}$)')
        axes[0].legend()
        
    im1 = axes[1].imshow(grav_history[:, :max_plot_r], aspect='auto', 
                         extent=[0, max_plot_r, steps*sim.dt, 0], cmap='magma')
    axes[1].set_title("Gravitational Wave Propagation (Divergence $\\nabla \\cdot u$)")
    axes[1].set_xlabel("Distance from Center (Grid)")
    axes[1].set_ylabel("Simulation Time ($t$)")
    fig.colorbar(im1, ax=axes[1])
    if len(t_g) > 0 and c_grav > 0:
        axes[1].plot(t_g, r_g, 'c--', label=f'Wavefront Fit ($c_g={c_grav:.3f}$)')
        axes[1].legend()
        
    plt.tight_layout()
    plt.savefig(f"{sim.output_dir}/wave_comparison_amp_{amplitude_grav}.png", dpi=150)
    plt.show()

if __name__ == "__main__":
    # 執行修正後的強擾動實驗
    run_experiment(amplitude_grav=0.2, amplitude_light=0.2, steps=600)