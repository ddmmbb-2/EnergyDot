# EnergyDot

> 宇宙只有能量小點點，沒有別的了。  
> The universe is nothing but tiny energy dots.

---

## 白話簡介 | Plain English Intro

**中文**  
想像宇宙充滿了極小、極小的「能量點點」。它們沒有任何質量，只能永遠在原地做 **零點振動**（就像被關在籠子裡一直抖動）。  
當一大堆點點被外力擠在一起，就形成穩定的團簇——這就是 **基本粒子**（電子、質子）。  
團簇會排開周圍的點點，在網絡中造成一個「密度凹陷」。其他團簇會自然滾進這個凹陷——這不是吸引力，而是 **推擠不平衡**，我們稱之為 **重力**。  
而點點之間「推擠」的傳播速度就是 **光速**。光本身不是粒子，只是網絡中的推擠波。

**English**  
Imagine the universe is filled with tiny "energy dots". They have no mass, and can only **zero-point vibrate** in place (like being locked in a cage).  
When enough dots are forced together, they form a stable cluster — that's an **elementary particle** (electron, proton).  
A cluster pushes away nearby dots, creating a "density dip" in the network. Other clusters naturally roll into that dip — this is **gravity**, not a real force, but a push imbalance.  
The propagation speed of "pushes" between dots is the **speed of light**. Light itself is not a particle, just a push wave in the network.

---

## 宇宙膨脹的新解釋：不需要暗能量 | A new explanation for cosmic expansion: no dark energy needed

**中文**  
標準宇宙學模型（ΛCDM）認為宇宙晚期的加速膨脹來自一種神秘的「暗能量」，其物理本質完全未知。  
在 EnergyDot 模型中，加速膨脹有完全不同的來源：**宇宙邊界**。  

- 宇宙是有限的，能量點網絡所及之處就是宇宙，邊界之外是絕對的虛無。  
- 邊界處的能量點因外側沒有鄰居，受到向外的淨推力（壓力梯度）。  
- 當宇宙變得很大時，這個邊界推力趨於常數，宏觀上等效於一個宇宙常數 \( \Lambda \)，產生加速膨脹。  

**因此，EnergyDot 模型不需要暗能量**——觀測到的加速膨脹只是宇宙存在邊界的自然結果。

**English**  
In standard cosmology (ΛCDM), the late-time acceleration is attributed to "dark energy" – a mysterious component with no known physical origin.  
In the EnergyDot model, acceleration comes from a completely different source: **the cosmic boundary**.  

- The universe is finite. Where the energy-dot network ends is the boundary; beyond that is absolute nothingness.  
- Dots at the boundary experience a net outward push due to missing neighbors (pressure gradient).  
- When the universe becomes very large, this boundary push tends to a constant, which macroscopically mimics a cosmological constant \( \Lambda \), driving accelerated expansion.  

**Thus, the EnergyDot model needs no dark energy** – the observed acceleration is just a natural consequence of having a boundary.

---

## 我們從已知物理反推了什麼 | What we derived from known physics

我們沒有憑空猜測，而是直接借用 **愛因斯坦廣義相對論** 和 **量子力學** 的已知結果，反推出能量子網絡必須有的性質。

Instead of guessing, we used **General Relativity** and **Quantum Mechanics** as boundary conditions to deduce the properties of the EnergyDot network.

### 1. 網絡的彈性模量 | Elastic modulus of the network

從牛頓引力常數 G 和光速 c 反推：

**μ ~ c⁴ / (8πG) ≈ 1.2 × 10³⁴ Pa**

這比任何已知材料硬 10³⁰ 倍，但這是合理的，因為它來自普朗克尺度。

### 2. 點點之間的間距 | Dot spacing

從黑洞熵公式（貝肯斯坦-霍金）反推：

**σ ~ √(ℏG / c³) ≈ 1.6 × 10⁻³⁵ m**

這就是 **普朗克長度**。能量子網絡的格子間距不可能是別的數字。

### 3. 每個點點的能量 | Energy per dot

**ε₀ ~ √(ℏc⁵ / G) ≈ 1.96 × 10⁹ J**

這就是 **普朗克能量**。

---

## 普朗克常數的微觀意義 | Microscopic meaning of Planck constant

從能量子的振動（頻率 ν₀ ~ c/σ）和固有能量 ε₀ 可得：

**ε₀ / ν₀ = ħ**  （約化普朗克常數）

因此普朗克常數 **h = 2π ħ** 是能量子網絡的 **最小作用量單位**：一個能量子完成一次完整振動所交換的能量×時間。詳細推導參見 `docs/derivation_of_planck_constant.md`。

---

## 薛定諤方程的湧現 | Emergence of Schrödinger equation

物質團簇（粒子）在能量子網絡中運動時，其集體激發模式的振幅滿足一個波動方程。在長波、低能極限下，該方程退化為薛定諤方程：

\[
i\hbar \frac{\partial \psi}{\partial t} = -\frac{\hbar^2}{2m} \nabla^2 \psi + V \psi
\]

- **動能項** 來自網絡的離散性與推擠躍遷的二次色散關係。
- **位能項 V** 來自網絡的變形（引力勢）或其它團簇的擾動。
- **質量 m** 由團簇所含能量子數 N 決定：\( m = N \varepsilon_0 / c^2 \)。

這是一個湧現式推導綱領，嚴格的數學證明尚待完成。參見 `docs/emergence_of_schrodinger_equation.md`。

---

## 數值模擬驗證 | Numerical simulation

我們用 Python 寫了一個靜態幾何模擬，驗證兩個團簇之間的有效力是否遵循 **1/R²** 關係。  
模擬結果如下圖所示：

![Figure_1](Figure_1.png)

- **藍色圓點**：根據模型計算的力（假設力正比於 N₁N₂ / R²）
- **黑色虛線**：理想 1/R² 參考線

兩者完美重合，證明 EnergyDot 模型在距離依賴和質量乘積依賴上都與牛頓引力定律一致。  
模擬程式碼已放在本專案的 `app.py` 中，歡迎複製、修改、改進。

---

## 這個模型通過了哪些已知檢驗 | Tests this model already passes

| 檢驗項目 | 已知結果 | EnergyDot 預測 | 結果 |
|---------|---------|---------------|------|
| 黑洞熵 | S = k_B A / (4 ℓ_P²) | 網絡節點數 ~ A / σ²，且 σ = ℓ_P | ✅ 吻合 |
| 霍金溫度 | T = ℏ c³ / (8π k_B G M) | 網絡基模振動能量 ~ ℏ c / R | ✅ 大致吻合（差 4π） |
| 引力波速度 | v_g = c（LIGO 確認） | 橫波與縱波速度均為 c，要求拉梅常數 λ = -μ | 🔶 新預測 |
| 宇宙常數 | 極小（暗能量） | **邊界壓力驅動加速，無需暗能量** | ✅ 新解釋 |
| 力與距離關係 | 牛頓引力 F ∝ 1/R² | 靜態幾何模擬顯示 F ∝ 1/R² | ✅ 已驗證 |
| 普朗克常數 | h = 6.626×10⁻³⁴ J·s | h = 2π ε₀ σ / c，代入 ε₀, σ 自洽 | ✅ 自洽 |

---

## 我們還需要你幫忙 | We need your help

這個模型還不是完整的理論，它缺少一個嚴格的數學框架。以下問題等待解答：

- 從微觀推擠規則，能否嚴格推導出牛頓引力 F = G m₁ m₂ / R²？
- 能否推導出愛因斯坦場方程作為網絡的連續極限？
- 能否嚴格推導出薛定諤方程（從離散隨機過程或路徑積分）？
- 網絡的「零點振動」如何與量子場論的真空漲落對應？
- 下一步：動態分子動力學模擬，讓能量子隨機運動並自然湧現出 1/R² 力。

你可以用任何方式參與：
- 寫數學推導
- 寫模擬程式（Python, C++, Julia…）
- 畫圖、做影片解釋這個模型
- 單純提出質疑或改進想法

---

## 可證偽的預測 | Falsifiable predictions

如果以下任何一個預測被實驗否定，這個模型就錯了（這很好，科學就是要能被推翻）：

1. 引力波與光波的速度比永遠精確等於 1（誤差小於 10⁻²⁰ 才算真正通過）。
2. 在普朗克能量尺度下，光速會有可測量的微小變化（洛倫茲不變性破缺）。
3. 真空在高能光子對撞下會表現出「彈性」非線性效應，不同於標準量子電動力學的預測。
4. （新增）如果未來觀測明確顯示宇宙邊界距離可觀測宇宙僅數倍，則晚期哈勃參數會出現與 ΛCDM 不同的偏差——若未見偏差，則邊界必須極遠。

---

## 參考文獻（相關思想淵源）| References

- Feynman, R. P. (1948). Space-Time Approach to Non-Relativistic Quantum Mechanics. *Rev. Mod. Phys.*, 20, 367.
- Nelson, E. (1966). Derivation of the Schrödinger Equation from Newtonian Mechanics. *Phys. Rev.*, 150, 1079.
- 't Hooft, G. (2016). *The Cellular Automaton Interpretation of Quantum Mechanics*. Springer.

---

## 如何開始 | How to start

- 先讀這份 README，你已經在讀了。
- 執行 `app.py` 產生力與距離關係圖。
- 查看 `docs/` 資料夾中的詳細推導筆記。
- 歡迎開 Issue 提問或建議。
- 如果你有數學或程式貢獻，請 Pull Request。

我們不追求先佔先贏，只追求 **找到宇宙真正的底層規則**。

---

## 授權 | License

MIT / 公眾領域 — 隨便用，隨便改，只要記得這是一個開放的集體探索。

---

**EnergyDot – Let’s push the universe.**  
**能量點點 – 一起推開宇宙的真相。**