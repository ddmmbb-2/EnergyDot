# 🌌 EnergyDot

> 宇宙只有能量小點點，沒有別的了。
> The universe is nothing but tiny energy dots.

⚠️ **關於本專案**：這是一個基於「由底而上（Bottom-up）湧現物理」的**計算機玩具模型（Toy Model）**。本專案試圖探討一個大膽的假設：如果宇宙最底層只存在單一的「推擠」規則，我們能否在不預設任何古典幾何光學、牛頓力學或張量微積分的前提下，從網格的自發演化中「長」出現代物理學的核心定律？這是一場開放的科學探索，所有結論仍需持續接受嚴格檢驗。

---

## 🔥 最新突破 (2026-05)

### 1. 🌟 湧現 1919 年日食星光偏折（廣義相對論弱場驗證）

在 3D 動態晶格中，我們發現了從純量壓力場 $P(r)$ 湧現引力透鏡效應的機制。透過引入代表空間網格拉長的「平方耦合」，波動包在通過質量空洞旁的偏折斜率，精準達到了牛頓一階極限的 **2.01 倍**，完美重現了愛因斯坦對星光偏折幾何翻倍的歷史性預測。
📂 詳見：[`doc/Starlight_deflection/`]

### 2. 📐 嚴格解析推導牛頓 $1/R^2$ 與 $w \approx 407$ 預言

在「質量正比於半徑（ $m \propto R$ ，非體積）」的修正洞察下，僅用三塊積木（空間推擠、空洞排開、質能等價），完整閉環推導出牛頓引力 $F \propto 1/R^2$。並從引力實驗中無參數湧現了極端硬稀狀態方程 $w = P_0 / \rho_E \approx 407$。
📂 詳見：[`doc/gravity2/`]

---

## 📖 白話簡介 (Introduction)

**中文** 想像宇宙充滿了極小、極小的「能量點點」。它們沒有任何質量，只能永遠在原地做 **零點振動**（就像被關在籠子裡一直抖動）。

當一大堆點點被外力擠在一起，就形成穩定的團簇——這在宏觀上表現為 **基本粒子**（如電子、質子）。

團簇會排開周圍的點點，在網絡中造成一個「密度凹陷」。其他團簇會自然滾進這個凹陷——這不是神秘的吸引力，而是 **推擠不平衡**，我們稱之為 **重力**。

而點點之間「推擠」的傳播速度就是 **光速**。光本身不是粒子，只是網絡中的推擠波。

當團簇突然消失，凹陷回彈產生的漣漪就是 **重力波**，它以光速向外傳播。

一個靜止團簇的凹陷深度（半徑）與其周圍儲存的彈性能量之間存在線性關係，這正是  $E = mc^2$  的微觀幾何起源——質量只是凍結的能量。

**English** Imagine the universe is filled with tiny "energy dots". They have no mass, and can only **zero-point vibrate** in place.

When enough dots are forced together, they form a stable cluster — manifesting macroscopically as an **elementary particle**.

A cluster pushes away nearby dots, creating a "density dip" in the network. Other clusters naturally roll into that dip — this is **gravity**, not a real attractive force, but a mechanical push imbalance.

The propagation speed of "pushes" between dots is the **speed of light**. Light itself is not a particle, just a push wave in the network.

When a cluster suddenly disappears, the dip rebounds, sending out ripples — **gravitational waves** — traveling at light speed.

For a static cluster, the depth of the dip (radius) is linearly related to the stored elastic energy: that's **$E = mc^2$** — mass is simply frozen energy.

---

## 🌌 宇宙膨脹的幾何解釋：或許不需要暗能量

標準宇宙學模型（$\Lambda\text{CDM}$）認為宇宙晚期的加速膨脹來自一種神秘的「暗能量」。但在 EnergyDot 玩具模型中，加速膨脹可以有一個非常樸素的力學來源：**宇宙邊界**。

* 如果能量點網絡（宇宙）是有限的，邊界之外是絕對的虛無。
* 邊界處的能量點因外側沒有鄰居，自然會受到向外的淨推力（壓力梯度）。
* 當宇宙變得極大時，這個邊界推力趨於常數，在宏觀上等效於一個宇宙常數 $\Lambda$，從而驅動加速膨脹。這提供了一個無需引入未知實體的替代思考方向。

---

## 🎯 玩具模型已成功重現的物理現象

儘管這只是一個底層演算法極度簡單的 3D 彈性晶格，我們已經成功在模擬環境中觀察到以下宏觀物理定律的「自發湧現」：

### 1. 三大相對論基石

* **光速不變**：測得脈衝壓力波速恆定為 $c = 0.31545$ 格/步（誤差 $0.245\%$）。
* **引力波速與光速一致**：粒子湮滅產生的能量密度波前，實測速度 $v_g / c = 98.6\%$。
* **質能等價**：實測缺陷能量 $\propto$ 缺陷半徑，比例常數精確對應 $c^2$（誤差 $3.4\%$）。

### 2. 引力場與黑洞幾何

* **牛頓萬有引力**：三維動態晶格中 $F \propto 1/R^2$ 嚴格自發湧現，並測出符合點缺陷有限尺寸預言的「近場修正偏離」。
* **萬有引力常數閉環**：$G = \mu / (4\pi \eta^2)$ 完全由微觀彈性參數推導得出。
* **靜態時空彎曲**：向量位移場在 $\nabla^2 \mathbf{u} = 0$ 靜態極限下，網格線自發彎曲成史瓦西度規的弱場圖像。

### 3. 星光偏折（引力透鏡）

* **$1/r$ 弱場定律**：證明純量壓力場 $P(r)$ 的下降會調製局部推擠波速，完美形成 $\Delta \theta \propto 1/r$ 的光線偏折。
* **廣義相對論 2x 幾何翻倍**：引入代表空間網格拉長的平方耦合後，實測偏折斜率精準達到單純時間膨脹效應的 **2.01 倍**。

---

## 🗺️ 開發路線圖 (Roadmap)

我們將計畫分為幾個階段，逐步從古典力學過渡到相對論，最終目標是觸碰量子力學的邊界：

* [x] **第一階段**：反推網絡常數，靜態幾何假設下驗證 $1/R^2$。
* [x] **第二階段**：三維動態晶格建立，湧現光速、引力波速、質能等價。
* [x] **第三階段**：嚴格解析推導引力常數 $G$、黑洞靜態時空彎曲與 $w \approx 407$ 預言。
* [x] **第四階段**：突破「散度陷阱」，重現愛因斯坦 1919 日食星光偏折與 2 倍幾何放大。
* [ ] **第五階段（進行中）**：動態時空模擬。引入雙星互繞系統，嘗試從晶格形變中提取引力波的四極矩波形。
* [ ] **第六階段**：分子動力學徹底隨機化。打破固定晶格，讓能量點真正隨機運動，觀察是否能自動凝聚成團簇。
* [ ] **第七階段**：量子力學湧現。嚴格推導團簇集體激發的振幅是否滿足薛丁格方程（Schrödinger Equation）。

---

## 🔬 可證偽的預測 (Falsifiable Predictions)

一個好的物理模型必須能夠被實驗推翻。如果以下任一現象被觀測否定，本模型即被證偽：

1. **引力波速極限**：引力波與光波的速度比永遠精確等於 1。
2. **普朗克尺度色散**：在接近普朗克能量尺度下，光速會有可測量的微小變化（洛倫茲不變性破缺）。
3. **真空非線性效應**：真空在極高能光子對撞下，會表現出有別於標準 QED 預測的「彈性」非線性碰撞效應。
4. **近場引力偏離**：微觀尺度下的引力近場 $1/R^2$ 偏離曲線，必須符合本模型預言的「點缺陷有限尺寸鈍化」形式。

---

## 🤝 參與探索 (How You Can Help)

這是一個業餘且開放的科學探索專案。無論你是物理學家、數學家、程式設計師或單純的愛好者，我們都非常需要你的幫助來「找碴」與推進：

* **數學審閱**：審查 [`doc/gravity2/`](https://www.google.com/search?q=doc/gravity2/) 中的解析推導，尋找邏輯漏洞或可改進的數學表述。
* **演算法優化**：目前的 3D CUDA 模擬極度吃重 GPU 記憶體頻寬，歡迎提供更高效的 FDTD 或格子波茲曼（LBM）優化方案。
* **推導連續極限**：協助從離散的非線性推擠規則出發，用粗粒化方法推導並證明其收斂於愛因斯坦真空場方程。
* **文獻對比**：找出與「彈性網絡湧現引力」、「類比引力 (Analogue Gravity)」相關的學術論文進行對比與整理。

歡迎直接開 Issue 提問質疑、發送 Pull Request，或單純分享你的改進想法！

---

## 📚 相關思想淵源 (References)

本模型的靈感與概念建立在許多前輩物理學家的探索之上：

* Feynman, R. P. (1948). Space-Time Approach to Non-Relativistic Quantum Mechanics.
* Nelson, E. (1966). Derivation of the Schrödinger Equation from Newtonian Mechanics.
* Sakharov, A. D. (1967). Vacuum quantum fluctuations in curved space and the theory of gravitation. (感應引力 Induced Gravity)
* Barceló, C., Liberati, S., & Visser, M. (2005). Analogue gravity. *Living Reviews in Relativity*.
* 't Hooft, G. (2016). *The Cellular Automaton Interpretation of Quantum Mechanics*.

---

## 🚀 快速開始 (Quick Start)

我們不追求先佔先贏，只追求 **找到宇宙真正的底層規則**。

1. 閱讀 **完整理論推導**：[`doc/gravity2/`](https://www.google.com/search?q=doc/gravity2/)
2. 閱讀 **星光偏折實驗報告**：[`Starlight_deflection/Starlight_deflection.md`](https://www.google.com/search?q=Starlight_deflection/Starlight_deflection.md)
3. 執行 **星光偏折 GPU 模擬**：`python Starlight_deflection/einstein_gravity_lens.py`（需 NVIDIA GPU + CuPy）
4. 執行 **黑洞時空彎曲模擬**：`python visualize_spacetime.py`
5. 執行 **三大相對論基石實驗**：進入 `doc/light/` 執行相關腳本。

---

## 📜 授權 (License)

MIT / 公眾領域 — 隨便用，隨便改，只要記得這是一個開放的集體探索。
