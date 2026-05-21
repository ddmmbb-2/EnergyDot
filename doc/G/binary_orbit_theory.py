import numpy as np
import matplotlib.pyplot as plt

# 校准常数
c = 0.3155          # 格/步
G = 0.8204          # 格^3/(步^2 * 质量)
M1 = M2 = 3.0       # 质量 = 半径
mu = M1 * M2 / (M1 + M2)
a = 10.0            # 轨道半径 (半长轴，每星到质心距离)
d = 2 * a           # 间距

# 圆轨道角速度
omega = np.sqrt(G * (M1 + M2) / d**3)
print(f"轨道角速度 ω = {omega:.5f} rad/步")
print(f"轨道周期 T = {2*np.pi/omega:.1f} 步")

# 引力波功率
P_theory = (32/5) * (G / c**5) * (mu**2) * (a**4) * (omega**6)
print(f"理论引力波功率 P = {P_theory:.4e} (能量单位/步)")

# 模拟持续时间建议 (1/4周期)
n_steps = int(0.25 * 2*np.pi/omega)
print(f"建议模拟步数: {n_steps} 步 (约1/4周期)")

# 绘制轨道
t = np.linspace(0, 2*np.pi/omega, 200)
x1 = a * np.cos(omega*t)
y1 = a * np.sin(omega*t)
x2 = -a * np.cos(omega*t)
y2 = -a * np.sin(omega*t)

plt.figure(figsize=(6,6))
plt.plot(x1, y1, 'b-', label='Star1')
plt.plot(x2, y2, 'r-', label='Star2')
plt.plot(0,0,'ko', label='Center of mass')
plt.xlabel('x (grids)')
plt.ylabel('y (grids)')
plt.title('Binary orbit (a=10, M=3 each)')
plt.axis('equal')
plt.grid(True)
plt.legend()
plt.savefig('binary_orbit_plot.png')
plt.show()