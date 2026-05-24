# 🌌 EnergyDot

> **宇宙只有能量小點點，沒有別的了。**
> The universe is nothing but tiny energy dots.

---

## 🚧 當前開發狀態：底層宇宙引擎重構中

本專案目前為一個處於早期開發階段的**物理玩具模型（Toy Model）**。我們目前正全力專注於建構最嚴謹的第一性原理底層宇宙代碼（`energydot_engine.py`）。

在過去的實驗與推導中，本模型目前最為可靠且已確立的核心基石為：


$$m \propto R$$

至於其他的進階物理現象（如大一統微極彈性、電磁場湧現、孤子動力學、波粒二象性等），我們將在底層引擎的數學與數值穩定性完全確立後，再重新進行嚴格的實驗驗證。目前的開發重心完全放在「讓一顆最基本的粒子在晶格中完美且穩定地存在」。

---

## 🚀 核心洞察：質量即幾何缺陷

EnergyDot 是一個挑戰「基本力本質」的計算模型。我們試圖推翻「超距作用」的假設，屏棄所有唯象經驗參數，探討一個核心命題：**如果宇宙只是一個純粹的 3D 彈性晶格，巨觀物理定律能否自發湧現？**

### 核心結論：質量的拓撲本質

$$m \propto R$$

本模型揭示了物質（質量 $m$）並非空間中的內稟實體，而是彈性網絡中「被排開的空間尺度（拓撲空洞半徑 $R$）」。質量即是幾何缺陷，而能量即是維持該缺陷不被撫平所需的彈性勢能，此純幾何推導自然指涉了 $E=mc^2$ 的底層起源。

---

## 📖 白話簡介 (Introduction)

**中文** 想像宇宙充滿了極小、極小的「能量點點」。它們沒有任何質量，只能永遠在原地做 **零點振動**（就像被關在籠子裡一直抖動）。

當一大堆點點被外力極端擠壓，跨越了晶格的拓撲障礙後，就會形成穩定的死結（團簇）——這在宏觀上表現為 **基本粒子**（如電子、夸克）。

團簇會排開周圍的點點，在網絡中造成一個「密度凹陷」。其他團簇會自然滾進這個凹陷——這不是神秘的超距吸引力，而是 **推擠不平衡**，我們稱之為 **重力**。

而點點之間「推擠」的傳播速度就是 **光速**。光本身不是實體粒子，只是網絡中的推擠應力波。

一個靜止團簇的凹陷深度（半徑）與其周圍鎖定的彈性能量之間存在線性關係，這正是 $E = mc^2$ 的微觀幾何起源——質量，不過是被拓撲凍結的能量。

**English** Imagine the universe is filled with tiny "energy dots". They have no mass, and can only **zero-point vibrate** in place.

When enough dots are forced together past a topological threshold, they form a stable knot (cluster) — manifesting macroscopically as an **elementary particle**.

A cluster pushes away nearby dots, creating a "density dip" in the network. Other clusters naturally roll into that dip — this is **gravity**, not a real attractive force, but a mechanical push imbalance.

The propagation speed of "pushes" between dots is the **speed of light**. Light itself is not a particle, just a push wave in the network.

For a static cluster, the depth of the dip (radius) is linearly related to the stored elastic energy: that's **$E = mc^2$** — mass is simply topologically frozen energy.

---

## 🎯 理論目標與待驗證現象 (Theoretical Targets)

以下現象是本模型在先前的迭代中曾觀察到、或理論上預言的現象。我們將在 `energydot_engine.py` 引擎重構完成後，逐一將其重新驗證並轉化為堅實的科學數據：

1. **大一統微極彈性引擎**：正式導入「微極彈性力學（Micropolar Elasticity）」，將推擠位移場 $\vec{u}$ 與原地扭轉場 $\vec{\theta}$ 透過旋度（Curl）互相耦合，尋求電磁場與引力場的純幾何統一。
2. **拓撲孤子飛行與量子波粒二象性**：引入 Sine-Gordon 非線性恢復力 $\beta \sin(u)$，驗證能量波包能否自我束縛成穩定的「拓撲孤子」在空間中飛行，並在極端撞擊下展現波的干涉與碎裂。
3. **量子質量譜與真空質量間隙**：在高精度的微觀晶格掃描中，驗證拓撲質量的增長是否呈現階梯狀的「量子化躍遷」，以及能量不足時自發湧現的「真空質量間隙（Mass Gap）」。
4. **宇宙膨脹的幾何邊界效應**：探討有限晶格宇宙邊界的壓力梯度，是否能提供一個等效於宇宙常數 $\Lambda$ 的淨推力，從而解釋加速膨脹而無需引入「暗能量」。

---

## 🗺️ 專案路線圖 (Roadmap)

| 階段 | 目標 | 狀態 |
| --- | --- | --- |
| **第一階段** | **基礎湧現**：確立 $m \propto R$ 核心原則，靜態幾何假設下驗證 $1/R^2$ 力律與 $E=mc^2$。 | ✅ 已確立 |
| **第二階段** | **底層引擎重構**：開發純粹基於第一性原理的 CUDA/CuPy 3D 演化引擎 (`energydot_engine.py`)。 | 🔶 進行中 |
| **第三階段** | **基態粒子淬鍊**：透過約束能量極小化（Relaxation），尋找並驗證第一顆永不衰變的完美基態電子。 | 🔶 進行中 |
| **第四階段** | **孤子動力學**：克服德里克定理（Derrick's Theorem）導致的坍縮，實現帶自旋粒子的穩定空間飛行。 | 📋 規劃中 |
| **第五階段** | **相對論與場論對接**：精準測量光速不變性，並重現引力透鏡偏折與非彈性碰撞碎片。 | 📋 規劃中 |

---

## 🤝 參與探索 (How You Can Help)

這是一個業餘且極度開放的科學探索專案。我們目前最迫切需要的是在**底層架構**上的協助。無論你是計算物理學家、數學家、程式設計師或單純的愛好者，我們都非常需要你的幫助來「找碴」與推進：

* **孤子穩定性與拓撲學**：協助尋求在 3D 離散晶格中對抗 Derrick's Theorem 坍縮的數學與物理機制（如 Skyrme term 或 Hopfion 環）。
* **數值 PDE 優化**：目前的 GPU 模擬在處理高頻空間差分時可能存在數值各向異性，歡迎提供更高階的差分模板或譜方法（Spectral method）建議。
* **數學審閱**：嚴格檢視非線性微極彈性方程式的能量動量守恆性。

歡迎直接開 Issue 提問質疑、發送 Pull Request，或單純分享你的改進想法！

---

## 📜 授權 (License)

MIT / 公眾領域 — 隨便用，隨便改，只要記得這是一個開放的集體探索。
