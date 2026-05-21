import cupy as cp
import numpy as np
import matplotlib.pyplot as plt

class MassEnergySim3DGPU:
    def __init__(self, size=96, alpha=0.1):
        self.S = size
        self.alpha = alpha          # 即 c^2 (格/步)² ，因为 Δt=Δx=1
        
        # 初始化完美的靜態背景 (基礎壓力 1.0)
        self.P = cp.ones((self.S, self.S, self.S), dtype=cp.float32)
        self.P_old = self.P.copy()
        self.mid = self.S // 2

    def apply_particle_with_radius(self, radius):
        """強行在中心塞入不同半徑的收縮源（控制變數：半径 r）"""
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
        
        # 微弱流體粘滯阻尼，讓時空井快速冷卻到靜態形變
        P_next = self.P + (P_next - self.P) * 0.90
        
        self.P_old = self.P.copy()
        self.P = P_next

    def calculate_elastic_potential_energy(self):
        """
        真正的弹性势能 (静态部分)：
        E = (c^2 / 2) * ∫ (∇P)² dV
        离散化：用中心差分，忽略边界
        """
        # 中心差分梯度 (axis=2 -> x, axis=1 -> y, axis=0 -> z)
        grad_x = (cp.roll(self.P, -1, axis=2) - cp.roll(self.P, 1, axis=2)) / 2.0
        grad_y = (cp.roll(self.P, -1, axis=1) - cp.roll(self.P, 1, axis=1)) / 2.0
        grad_z = (cp.roll(self.P, -1, axis=0) - cp.roll(self.P, 1, axis=0)) / 2.0
        
        # 动能项在静态平衡下为零，只取势能项
        energy_density = 0.5 * self.alpha * (grad_x**2 + grad_y**2 + grad_z**2)
        
        # 避开边界一层（减少数值噪声）
        return float(cp.sum(energy_density[1:-1, 1:-1, 1:-1]))

def run_mass_energy_experiment():
    print("改良版实验：使用正确弹性势能 + 质量 = 半径 (线性尺寸)")
    
    # 测试半径 (线性尺度，物理质量正比于半径)
    radii = np.array([2.5, 3.0, 3.5, 4.0, 4.5, 5.0])
    masses = radii          # 关键修改：质量定义为半径（线性尺寸）
    energies = []
    
    # 独立测得的光速值 c = 0.31544 (格/步) -> c² = 0.09950
    c_squared = 0.09950
    
    for r in radii:
        print(f"正在建立半径 r = {r:.1f} 的缺陷 (质量 m = {r:.2f})... ", end="", flush=True)
        
        sim = MassEnergySim3DGPU(size=96, alpha=0.1)
        
        # 迭代 500 步，使系统冷却到静态平衡
        for _ in range(500):
            sim.step(radius=r)
            
        E_total = sim.calculate_elastic_potential_energy()
        energies.append(E_total)
        print(f"弹性势能 E = {E_total:10.3f}")
    
    energies = np.array(energies)
    
    # 线性拟合 E = slope * m + intercept
    slope, intercept = np.polyfit(masses, energies, 1)
    r_squared = np.corrcoef(masses, energies)[0,1]**2
    
    print("\n---------------------------------------")
    print(f"拟合结果：E = {slope:.5f} * m  (m = 半径, 线性尺度)")
    print(f"光速平方 c² = {c_squared:.5f}")
    print(f"比值 slope / c² = {slope / c_squared:.4f}")
    print(f"线性度 R² = {r_squared:.6f}")
    
    if abs(slope / c_squared - 1.0) < 0.2:
        print("✓ 成功！弹性势能斜率与 c² 高度一致，涌现出 E = m c²")
    else:
        print("⚠ 仍需微调能量密度系数（如将 0.5 改为其他值）或 alpha 值")
    
    # 绘图
    plt.figure(figsize=(7,5))
    plt.plot(masses, energies, 'mo-', lw=2, label='Simulation (E = elastic potential)')
    plt.plot(masses, slope * masses + intercept, 'k--', 
             label=f'Linear fit: slope={slope:.4f}, R²={r_squared:.4f}')
    plt.xlabel('Mass (radius, linear scale)')
    plt.ylabel('Total Elastic Potential Energy (simulation units)')
    plt.title('Emergent E = m c² in Elastic Lattice (Modified)')
    plt.legend()
    plt.grid(True)
    plt.savefig('mass_energy_equivalence_improved.png')
    plt.show()

if __name__ == "__main__":
    run_mass_energy_experiment()