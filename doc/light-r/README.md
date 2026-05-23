# 🌌 EnergyDot Universe Simulator

EnergyDot 是一個基於「由底而上（Bottom-up）湧現物理」的 3D 彈性晶格宇宙模型。

本專案完全拋棄標準模型（Standard Model）中帶有經驗參數的唯象公式，也不直接套用廣義相對論（General Relativity）的數學框架。我們堅守最底層的**純幾何與波動力學**，透過 3D 彈性網格的形變干涉，在電腦中「自然湧現」出萬有引力、電磁學、量子質量階層與波粒二象性。

## ⚛️ 第一性原理 (First Principles)

1. **巴克球宇宙 (The Buckyball Vacuum)**：宇宙空間並非虛無，而是由緊密排列的能量小點點（類似巴克球）構成的 3D 彈性晶格。它們不能隨意自由移動，所有的物理現象皆為這套晶格網路的形變、應力波或拓撲缺陷。
2. **無超距作用 (No Spooky Action at a Distance)**：拒絕超距力。所有的基本作用力（引力、電磁力）皆為純幾何形變在晶格中傳遞的波動干涉。
3. **質量的拓撲本質 (Topological Mass)**：物質不是點，而是排開空間的「拓撲空洞」。慣性質量與空洞半徑成正比（$m \propto R$）。能量是維持該缺陷不被真空壓平的彈性勢能，從而自然湧現 $E=mc^2$，且從根本上消滅了無限大奇點。

---

## 📁 專案目錄結構

目前專案分為「穩定版測試」與「大一統先進引擎（位於 `test/` 目錄）」兩部分：

```text
light-r/
│
├── lattice_core.py                 # (v1.0) 基礎 3D 向量場引擎
├── test_legacy_experiments.py      # 古典實驗：光速測量、重力波前、E=mc^2 驗證
├── quantum_mass_spectrum.py        # 量子力學實驗：晶格量子化與質量間隙探測
├── *.csv / *.png                   # 自動生成的實驗數據與軌跡圖表
│
└── test/                           # 🚀 (v2.0) 大一統微極彈性與非線性動力學實驗室
    ├── lattice_core.py             # 核心升級：Cosserat 微極彈性 + Sine-Gordon 非線性孤子
    ├── composite_electron.py       # 複合電子生成器（質量 + 電荷 + 自旋耦合）
    ├── soliton_flight.py           # 拓撲孤子自由飛行實驗
    └── soliton_collision.py        # 波粒二象性實驗：非線性波包的高速撞擊與破碎

```

---

## ⚙️ 核心引擎技術：微極彈性大一統

在 `test/lattice_core.py` 的最新引擎中，我們成功實現了雙場耦合的宇宙：

* **推擠位移場 $\vec{u}$**：負責質量排擠、萬有引力與純量波（極限傳遞速度即為光速/重力波速）。
* **原地扭轉場 $\vec{\theta}$**：引入微極彈性力學（Micropolar Elasticity），賦予晶格旋轉自由度，負責產生自旋、磁場渦旋與橫波（電磁輻射）。
* **齒輪耦合 ($\kappa$)**：推擠與自旋透過彼此的旋度（Curl）互相咬合轉換，完美湧現出安培環路定律與座標系拖曳（Frame-dragging）。
* **孤子非線性 ($\beta \sin(u)$)**：引入非線性恢復力，使能量波包能自我束縛成「拓撲孤子（Topological Solitons）」，打破線性波的色散，賦予粒子在空間中維持形狀自由飛行的能力。

---

## 🧪 經典實驗里程碑

如果你想親眼見證物理定律的湧現，請執行以下腳本：

### 1. 量子質量譜 (Quantum Mass Spectrum)

`python quantum_mass_spectrum.py`

* **成果**：證明在離散的 3D 晶格下，質量的增長不是平滑的，而是呈現階梯狀的量子化躍遷。同時證實了「真空質量間隙（Mass Gap）」的存在——能量不足以撐開 1 格空間的擾動，無法形成穩定粒子。

### 2. 複合電子湧現 (Emergence of the Electron)

`cd test && python composite_electron.py`

* **成果**：在空間中心同時注入排擠（質量）、向內拉扯（負電荷散度）與 Z 軸自旋。引擎在無麥克斯韋方程的干預下，自發激發出向內的庫倫電場，以及由自旋捲動空間產生的「完美磁偶極漩渦」。

### 3. 波粒二象性與非彈性撞擊 (Wave-Particle Duality)

`cd test && python soliton_collision.py`

* **成果**：展示非線性波包（粒子）在空間中直線飛行。當其遭遇無限大質量的牆壁時，展現出波動本性的劇烈干涉，最終因能量過載而超越非線性束縛極限，碎裂成四散的能量碎片（模擬高能粒子對撞的非彈性散射）。

---

## 🛠️ 環境依賴

* Python 3.8+
* CuPy (需要 NVIDIA GPU 進行 3D 晶格平行運算加速)
* NumPy
* Matplotlib

## 🔮 未來展望

目前 EnergyDot 已具備靜態拓撲缺陷與動態孤子飛行的能力。下一步將挑戰：

1. 雙狹縫干涉的幾何模擬。
2. 夸克禁閉（多缺陷旋轉駐波鎖定）與動態原子軌域的湧現。

