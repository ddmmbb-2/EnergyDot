"""
EnergyDot 最簡模擬：兩個團簇之間的力與距離關係
使用靜態幾何近似（非動態模擬）
"""

import numpy as np
import matplotlib.pyplot as plt

print("開始 EnergyDot 模擬...")

# 參數設定
N1 = 10   # 團簇 A 包含的能量子數
N2 = 10   # 團簇 B 包含的能量子數
R_range = np.logspace(-35, -30, 20)  # 距離範圍 (m)

# 模擬力的大小：按照我們推導的模型，力正比於 (N1 * N2) / R^2
# 這裡我們把比例常數設為 1，只觀察形狀
def effective_force(R):
    return (N1 * N2) / (R**2)

# 計算每個距離的力
forces = [effective_force(R) for R in R_range]

# 繪圖
plt.figure(figsize=(8,5))
plt.loglog(R_range, forces, 'o-', linewidth=2, label=f'N1={N1}, N2={N2}')
plt.xlabel('距離 R (m)')
plt.ylabel('淨力 (任意單位)')
plt.title('EnergyDot 預測的引力與距離關係')
plt.grid(True)

# 畫一條 1/R^2 參考線，驗證斜率
ref_R = np.logspace(-35, -30, 20)
ref_F = 1 / ref_R**2
ref_F = ref_F / ref_F[0] * forces[0]  # 歸一化到相同起點
plt.loglog(ref_R, ref_F, 'k--', label='1/R² 參考線')
plt.legend()
plt.savefig('force_vs_distance.png')
print("圖形已儲存為 force_vs_distance.png")
plt.show()

print("模擬完成！")