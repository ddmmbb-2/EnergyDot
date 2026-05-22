import numpy as np
from energy_dot_lattice_3d import EnergyLatticeSim3DGPU

def run_G_constant_calculation():
    print("🚀 啟動 EnergyDot 計畫 B：大一統常數對接與 ρ_E 計算...")
    
    # 1. 物理參數設定
    R_distance = 40.0        # 確保在遠場區 (1/R^2 成立的區域)
    R_void = 4.5             # 空洞半徑 (質量 M)
    alpha_mu = 0.08          # 彈性模量 (程式中的 alpha)
    c_sim = np.sqrt(alpha_mu)# 模擬宇宙中的光速 (波動傳遞速度)
    
    print(f"   [系統參數] 空洞質量 M_A = M_B = {R_void}")
    print(f"   [系統參數] 測試距離 R = {R_distance}")
    print(f"   [系統參數] 彈性模量 μ = {alpha_mu}, 光速 c = {c_sim:.4f}")
    
    # 2. 執行 V3 3D 連續晶格模擬
    print("   [運算中] 正在 V3 晶格中沉澱壓力場 (900步)... ", end="", flush=True)
    sim = EnergyLatticeSim3DGPU(size=96, alpha=alpha_mu)
    
    # 設定空洞位置
    sim.cA_x = sim.S // 2 - int(R_distance) // 2
    sim.cB_x = sim.S // 2 + int(R_distance) // 2
    
    for _ in range(900):
        sim.step()
        
    F_sim = sim.measure_net_force_3d()
    print(f"完成！\n   => 測得淨推力 F = {F_sim:.6f}")
    
    # 3. 核心物理對接計算
    print("\n==================================================")
    print(" 🌌 EnergyDot 宇宙常數揭曉 🌌")
    print("==================================================")
    
    # 計算模擬宇宙的 G 值
    # F = G * (M_A * M_B) / R^2  =>  G = F * R^2 / (M_A * M_B)
    G_sim = (F_sim * (R_distance**2)) / (R_void * R_void)
    print(f" [1] 湧現的萬有引力常數 G_sim = {G_sim:.6f}")
    
    # 驗證 k 值 (質量與體積/半徑的轉換常數)
    # 根據推導： G = μ / (4π k^2)  =>  k = sqrt(μ / (4π G))
    k_sim = np.sqrt(alpha_mu / (4 * np.pi * G_sim))
    print(f" [2] 幾何質量轉換常數 k = {k_sim:.6f}")
    
    # 計算背景真空能量密度 ρ_E
    # 根據推導： k = ρ_E / c^2  =>  ρ_E = k * c^2
    rho_E_sim = k_sim * (c_sim**2)
    print(f" [3] 預言的真空能量密度 ρ_E  = {rho_E_sim:.6f}")
    print("==================================================\n")
    
    print("總設計師，這就是你的宇宙底層代碼。")
    print("只要你知道了 ρ_E，你就能算出每一顆微觀能量點到底蘊含多少純粹的能量！")

if __name__ == "__main__":
    run_G_constant_calculation()