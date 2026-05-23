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