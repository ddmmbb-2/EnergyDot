import cupy as cp
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import detrend
from scipy.optimize import curve_fit

class HarmonicGWSim:
    def __init__(self, size=400, alpha=0.1, M1=3.0, M2=3.0, a=60.0):
        self.S = size
        self.alpha = alpha
        self.c = np.sqrt(alpha)
        self.G = 0.8204
        self.M1, self.M2 = M1, M2
        self.a = a
        self.d = 2*a
        self.omega = np.sqrt(self.G * (M1+M2) / self.d**3)
        self.mid = size // 2

        self.P = cp.ones((size, size, size), dtype=cp.float32)
        self.P_old = self.P.copy()

        # 吸收邊界（厚度 25 格）
        self.absorb = cp.ones((size, size, size), dtype=cp.float32)
        for i in range(25):
            f = np.exp(-0.08 * i)
            self.absorb[i,:,:] *= f; self.absorb[-i-1,:,:] *= f
            self.absorb[:,i,:] *= f; self.absorb[:,-i-1,:] *= f
            self.absorb[:,:,i] *= f; self.absorb[:,:,-i-1] *= f

    def apply_gaussian_masses(self, t, radius=2.5, depth=0.95):
        x1 = self.a * np.cos(self.omega * t)
        y1 = self.a * np.sin(self.omega * t)
        x2 = -x1; y2 = -y1
        for (x, y) in [(x1, y1), (x2, y2)]:
            ix = int(round(self.mid + x))
            iy = int(round(self.mid + y))
            iz = self.mid
            if not (radius <= ix < self.S-radius and radius <= iy < self.S-radius):
                continue
            zz, yy, xx = cp.ogrid[:self.S, :self.S, :self.S]
            dist2 = (zz-iz)**2 + (yy-iy)**2 + (xx-ix)**2
            sigma = radius / 2.0
            defect = depth * cp.exp(-dist2 / (2 * sigma**2))
            self.P = cp.minimum(self.P, 1 - defect)

    def step(self, t, radius=2.5):
        self.apply_gaussian_masses(t, radius)
        P_up = cp.roll(self.P, 1, axis=1)
        P_down = cp.roll(self.P, -1, axis=1)
        P_left = cp.roll(self.P, 1, axis=2)
        P_right = cp.roll(self.P, -1, axis=2)
        P_front = cp.roll(self.P, 1, axis=0)
        P_back = cp.roll(self.P, -1, axis=0)
        laplacian = (P_up+P_down+P_left+P_right+P_front+P_back - 6*self.P)
        
        # ❌ 阻尼代償徹底拔除！回歸 100% 完美的純粹波動方程
        P_next = 2*self.P - self.P_old + self.alpha * laplacian
        
        self.P_old = self.P.copy()
        self.P = P_next
        self.P *= self.absorb
        self.P_old *= self.absorb
        self.apply_gaussian_masses(t, radius)

def run_harmonic_analysis():
    print("=== 雙星宇宙終極演化：100% 零阻尼純真空大長征 ===")
    sim = HarmonicGWSim(size=400, a=60.0)
    
    # 安全的遠場天文台觀測陣列
    probe_radii = [80, 110, 140, 170]   
    probe_coords = [(sim.mid + r, sim.mid, sim.mid) for r in probe_radii]
    
    total_steps = 4000
    sample_interval = 2
    n_samples = total_steps // sample_interval
    
    signals = {r: [] for r in probe_radii}
    
    print(f"理論雙星角速度 ω = {sim.omega:.6f}")
    f_gw_theory = 2 * sim.omega / (2 * np.pi)
    print(f"理論四極矩引力波基頻 2ω = {f_gw_theory:.6f}")
    print(f"正在發動 3060 進行 4000 步【零阻尼】矩陣推演...")
    
    for step in range(total_steps):
        sim.step(float(step))
        if step % sample_interval == 0:
            for r, (px, py, pz) in zip(probe_radii, probe_coords):
                val = float(sim.P[pz, py, px]) - 1.0
                signals[r].append(val)
    
    results = {}
    plt.figure(figsize=(14, 10))
    
    for i, r in enumerate(probe_radii):
        sig = np.array(signals[r])
        
        # 剔除波前傳播死區
        arrival_time = int(1.2 * r / sim.c) // sample_interval
        sig_clean = sig[arrival_time:]
        if len(sig_clean) < 100:
            continue
        sig_detrend = detrend(sig_clean)
        
        # FFT
        dt = sample_interval
        freqs = fftfreq(len(sig_detrend), d=dt)
        spectrum = np.abs(fft(sig_detrend))
        pos = freqs > 0
        freqs_pos = freqs[pos]
        spectrum_pos = spectrum[pos]
        
        # 🔴 優化全域尋峰：避開直流漂移，精準捕捉能量最高峰
        peak_idx = np.argmax(spectrum_pos[2:]) + 2
        peak_freq = freqs_pos[peak_idx]
        
        amplitude = np.std(sig_detrend)
        results[r] = {'freq': peak_freq, 'amp': amplitude}
        print(f"探測半徑 r = {r:3d} : 實測主頻 {peak_freq:.6f} | 振幅 RMS = {amplitude:.3e}")
        
        # 繪圖
        plt.subplot(2, 2, i+1)
        plt.plot(freqs_pos, spectrum_pos, 'b-')
        plt.axvline(f_gw_theory, color='r', linestyle='--', label='Theory 2ω')
        plt.axvline(peak_freq, color='g', linestyle=':', label=f'Peak = {peak_freq:.5f}')
        plt.xlim(0, 0.01) # 聚焦超低頻精細結構
        plt.xlabel('Frequency (1/step)')
        plt.ylabel('Amplitude')
        plt.title(f'Zero-Damping Spectrum at r = {r}')
        plt.legend()
        plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('harmonic_analysis_zero_damping.png')
    plt.show()
    
    # 衰減冪律擬合
    radii = np.array(list(results.keys()))
    amps = np.array([results[r]['amp'] for r in radii])
    
    def power_law(r, A0, n):
        return A0 * r**(-n)
        
    try:
        popt, _ = curve_fit(power_law, radii, amps, p0=[1, 1])
        print("\n================ 零阻尼宇宙物理診斷 ================")
        print(f" 實測引力波振幅隨空間衰減指數 n = {popt[1]:.3f}")
        if abs(popt[1] - 1.0) < 0.2:
            print(" 🏆 1/r 輻射特性確立！這是一場毫無損耗、完美的真空引力輻射！")
        print("==================================================")
    except Exception as e:
        print(f"\n擬合失敗（可能受到非線性高頻干涉影響）: {e}")

if __name__ == "__main__":
    run_harmonic_analysis()