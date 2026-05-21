import numpy as np
import matplotlib.pyplot as plt
import cupy as cp
from scipy.optimize import curve_fit

class StaticGravitySim:
    """用于测量静态引力常数 G 的模拟器"""
    def __init__(self, size=128, alpha=0.1):
        self.S = size
        self.alpha = alpha          # c^2
        self.P = cp.ones((self.S, self.S, self.S), dtype=cp.float32)
        self.P_old = self.P.copy()
        self.mid = self.S // 2

    def apply_spherical_defect(self, radius):
        """在中心设置半径 radius 内的压力为 0（永久缺陷）"""
        z, y, x = cp.ogrid[:self.S, :self.S, :self.S]
        dist2 = (z - self.mid)**2 + (y - self.mid)**2 + (x - self.mid)**2
        mask = dist2 <= radius**2
        self.P[mask] = 0.0
        # 注意：此缺陷会被每次 step 覆盖，必须在每个 step 中重新应用

    def step(self, radius):
        """执行一次波动方程演化，并强制缺陷区域压力为 0"""
        # 先强制缺陷 (保证每一步缺陷形状不变)
        self.apply_spherical_defect(radius)

        # 拉普拉斯算子
        P_up    = cp.roll(self.P,  1, axis=1)
        P_down  = cp.roll(self.P, -1, axis=1)
        P_left  = cp.roll(self.P,  1, axis=2)
        P_right = cp.roll(self.P, -1, axis=2)
        P_front = cp.roll(self.P,  1, axis=0)
        P_back  = cp.roll(self.P, -1, axis=0)
        laplacian = (P_up + P_down + P_left + P_right + P_front + P_back - 6 * self.P)

        # 波动方程 + 轻度阻尼加速收敛到稳态
        P_next = 2 * self.P - self.P_old + self.alpha * laplacian
        P_next = self.P + (P_next - self.P) * 0.95   # 阻尼因子

        self.P_old = self.P.copy()
        self.P = P_next

        # 再次强制缺陷 (由于阻尼可能会略微改变边界)
        self.apply_spherical_defect(radius)

    def run_to_steady_state(self, radius, steps=800):
        """迭代直到压力场稳定"""
        print(f"模拟半径 R = {radius} 的静态质量，迭代 {steps} 步...")
        for _ in range(steps):
            self.step(radius)
        # 返回压力场的 CPU 副本
        return cp.asnumpy(self.P)

def gravitational_potential_fit(r, A):
    """牛顿势形式 phi = -A / r"""
    return -A / r

def calibrate_gravity_constant():
    print("=== 校准弹性晶格中的等效引力常数 G ===")

    # 已知光速（从 speed_of_light_final.py 获得）
    c_sim = 0.3155   # 格/步
    c2_sim = c_sim**2   # 约 0.09955

    # 测试不同的缺陷半径（质量）
    radii = np.array([3.0, 4.0, 5.0, 6.0], dtype=float)
    A_list = []

    plt.figure(figsize=(8, 6))

    for R in radii:
        sim = StaticGravitySim(size=128, alpha=0.1)
        P_field = sim.run_to_steady_state(R, steps=800)

        # 提取沿 x 轴（或 z 轴）的压力分布，并计算半径
        mid = sim.mid
        # 取从中心沿 x 正半轴的点
        x_axis = np.arange(mid, sim.S) - mid
        P_axial = P_field[mid, mid, mid:]   # 沿 x 正方向

        # 只考虑 r > R 的区域，且避开边界
        r_vals = x_axis[x_axis > R + 1.0]
        phi_vals = P_axial[x_axis > R + 1.0] - 1.0   # 扰动

        # 拟合 phi = -A / r
        try:
            popt, _ = curve_fit(gravitational_potential_fit, r_vals, phi_vals, p0=[R])
            A_fit = popt[0]
            A_list.append(A_fit)
            print(f"半径 R = {R:.1f}  -> 拟合 A = {A_fit:.5f}")

            # 绘图
            r_fit = np.linspace(R+1, 30, 100)
            plt.plot(r_vals, phi_vals, 'o', markersize=3, label=f'R={R}')
            plt.plot(r_fit, gravitational_potential_fit(r_fit, A_fit), '--',
                     label=f'Fit: -{A_fit:.3f}/r')
        except Exception as e:
            print(f"半径 {R} 拟合失败: {e}")
            continue

    plt.xlabel('r (grids)')
    plt.ylabel(r'$\varphi = P - 1$')
    plt.title('Static gravitational potential from spherical defect')
    plt.legend()
    plt.grid(True)
    plt.savefig('gravitational_potential_fits.png')
    plt.show()

    # 根据 A = G_sim * M，这里 M = R（质量正比于半径，比例系数已由 E=mc² 固定）
    masses = radii   # M = R
    A_array = np.array(A_list)

    # 拟合 A = G_sim * M  -> 斜率即为 G_sim
    G_sim, intercept = np.polyfit(masses, A_array, 1)
    r2 = np.corrcoef(masses, A_array)[0,1]**2

    print("\n=== 校准结果 ===")
    print(f"光速 c = {c_sim:.5f}  (格/步)")
    print(f"c² = {c2_sim:.5f}")
    print(f"质量定义为 M = 半径 (线性尺度)")
    print(f"拟合关系: A = G_sim * M  ->  G_sim = {G_sim:.5f}")
    print(f"线性度 R² = {r2:.6f}")

    # 与爱因斯坦场方程系数对比：弱场极限 ∇²φ = 4πGρ
    # 在我们的模拟中，单位长度 Δx=1，单位时间 Δt=1，压力无量纲。
    # 泊松方程应成立：∇²φ = source。source 由缺陷内部结构给出。
    # 对于球对称缺陷，内部 ∇²φ = -6/R²? 其实球内 φ=-1 满足拉普拉斯方程（除边界外），
    # 所以源项集中在球面上。但我们通过外部拟合得到的 G_sim 已经反映了等效常数。
    # 爱因斯坦场方程系数 8πG/c^4 在模拟中对应什么？可以计算：
    einstein_coeff = 8 * np.pi * G_sim / c2_sim**2   # c^4 在模拟单位中是 (c^2)^2
    print(f"\n爱因斯坦场方程中的组合系数 8πG/c⁴ = {einstein_coeff:.5e} (模拟单位)")

    # 验证泊松方程积分形式：对于质量 M，外部势 φ = -G_sim M / r
    # 则通过高斯定理 ∫∇²φ dV = 4πG_sim M，与连续方程一致。
    # 可以进一步输出模拟单位下的 G_sim 数值。
    print("\n提示：模拟单位下，长度=1格，时间=1步，压力无量纲，质量=半径(格)。")
    print(f"因此等效的牛顿引力常数 G = {G_sim:.5f}  (格³/(步²·质量单位))")

    # 绘制 A vs M 线性关系
    plt.figure(figsize=(6,5))
    plt.plot(masses, A_array, 'ro-', label='Measured A')
    plt.plot(masses, G_sim*masses + intercept, 'b--', label=f'Fit G={G_sim:.4f}, R²={r2:.5f}')
    plt.xlabel('Mass M = radius (grids)')
    plt.ylabel('Potential coefficient A = G·M')
    plt.title('Calibration of Gravitational Constant G')
    plt.grid(True)
    plt.legend()
    plt.savefig('gravity_constant_calibration.png')
    plt.show()

if __name__ == "__main__":
    calibrate_gravity_constant()