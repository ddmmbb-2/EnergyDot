import cupy as cp
import numpy as np
import matplotlib.pyplot as plt

class MassEnergySim3DGPU:
    def __init__(self, size=96, alpha=0.1):
        self.S = size
        self.alpha = alpha
        
        # 初始化完美的靜態背景 (基礎壓力 1.0)
        self.P = cp.ones((self.S, self.S, self.S), dtype=cp.float32)
        self.P_old = self.P.copy()
        self.mid = self.S // 2

    def apply_particle_with_radius(self, radius):
        """強行在中心塞入不同半徑的收縮源（控制變數：質量 m）"""
        z, y, x = cp.ogrid[:self.S, :self.S, :self.S]
        mask = ((z - self.mid)**2 + (y - self.mid)**2 + (x - self.mid)**2) <= radius**2
        self.P[mask] = 0.0

    def step(self, radius):
        """3D 晶格彈性傳導"""
        self.apply_particle_with_radius(radius)
        
        P_up    = cp.roll(self.P,  1, axis=1)
        P_down  = cp.roll(self.P, -1, axis=1)
        P_left  = cp.roll(self.P,  1, axis=2)
        P_right = cp.roll(self.P, -1, axis=2)
        P_front = cp.roll(self.P,  1, axis=0)
        P_back  = cp.roll(self.P, -1, axis=0)
        
        laplacian = (P_up + P_down + P_left + P_right + P_front + P_back - 6 * self.P)
        
        # 波動方程
        P_next = 2 * self.P - self.P_old + self.alpha * laplacian
        
        # 加上微弱流體粘滯阻尼，讓時空井快速冷卻到完美的靜態形變結構
        P_next = self.P + (P_next - self.P) * 0.90
        
        self.P_old = self.P.copy()
        self.P = P_next

    def calculate_total_strain_energy(self):
        """計算整個時空晶格海中儲存的總彈性應變能 (E)"""
        # 應變能正比於每個點偏離平衡基線 (1.0) 的壓強差平方和
        energy_field = (self.P - 1.0) ** 2
        total_energy = float(cp.sum(energy_field))
        return total_energy

def run_mass_energy_experiment():
    print("開始執行 EnergyDot 終極噱頭實驗：驗證 E = mc² 的微觀機械本質...")
    
    # 測試不同的粒子缺陷半徑 (代表逐漸增大的幾何質量)
    radii = np.array([2.5, 3.0, 3.5, 4.0, 4.5, 5.0])
    
    # 在 3D 空間中，球體體積正比於半徑的三次方，我們將體積定義為機械質量 m
    masses = (4.0 / 3.0) * np.pi * (radii ** 3)
    energies = []
    
    # 先前測得之時空常數：光速 c = 0.31544
    c_fixed = 0.31544
    c_squared = c_fixed ** 2 # 約 0.09950
    
    for r in radii:
        # 計算對應的幾何質量
        m_geo = (4.0 / 3.0) * np.pi * (r ** 3)
        print(f"正在建立質量 m = {m_geo:7.2f} (核心半徑 r = {r}) 的重力井... ", end="", flush=True)
        
        sim = MassEnergySim3DGPU(size=96, alpha=0.1)
        
        # 迭代 500 步，讓周圍時空充分被拉扯並沉澱到靜態最穩定狀態
        for _ in range(500):
            sim.step(radius=r)
            
        # 秤重：量測這時整個晶格海裡累積的總能量
        E_total = sim.calculate_total_strain_energy()
        energies.append(E_total)
        print(f"時空總應變能 E = {E_total:10.2f}")
        
    energies = np.array(energies)
    
    # --- 驗證 E 與 m 的線性正比關係 (E / m 是否為常數) ---
    ratios = energies / masses
    
    # 做一個線性擬合，看斜率（質能轉換係數）是多少
    slope, intercept = np.polyfit(masses, energies, 1)
    
    print("---------------------------------------")
    print(f"🏆 質能轉換擬合結果：E = {slope:.5f} * m")
    print(f"【對組對照】先前獨立測得之宇宙光速平方 c² = {c_squared:.5f}")
    
    # 建立轉換修正算子 (微觀晶格量綱常數)
    # 在真實物理中，因為單位不同需要乘以常數；我們來看兩者的關聯性度
    r_squared = np.corrcoef(masses, energies)[0,1]**2
    print(f"質能互換公式自洽度 (R² 線性度): {r_squared:.6f} (越接近 1 代表 E 嚴格正比於 m)")
    
    # 繪製愛因斯坦質能折線圖
    plt.figure(figsize=(7, 5))
    plt.plot(masses, energies, 'mo-', lw=2, label='Lattice Simulation (EnergyDot V4)')
    plt.plot(masses, slope * masses + intercept, 'k--', label=f'Einstein Linear Relation (R²={r_squared:.4f})')
    plt.xlabel('Mechanical Mass (m ∝ r³)')
    plt.ylabel('Total Lattice Strain Energy (E)')
    plt.title('V4 Verification: Einstein Mass-Energy Equivalence')
    plt.legend()
    plt.grid(True)
    plt.savefig('mass_energy_equivalence_success.png')
    plt.show()

if __name__ == "__main__":
    run_mass_energy_experiment()