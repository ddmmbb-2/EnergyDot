
# 🌌 EnergyDot: 3D Geometric Continuum Universe Engine

> **"The universe is nothing but tiny energy dots."**
> 宇宙本質上僅是由能量點構成的連續介質。

---

## 🚧 當前開發狀態
本專案為一個處於活躍開發階段的 **湧現物理模型 (Emergent Physics Model)**。我們致力於從第一性原理出發，透過 3D 彈性晶格模擬，觀察宏觀物理定律如何從底層結構中自發湧現。

### 核心科學推導
我們提出質量非內稟實體，而是拓撲缺陷：
$$m \propto R$$
其中 $m$ 為質量，$R$ 為能量點網絡中的拓撲空洞半徑。這揭示了質量即是幾何缺陷，而能量即是維持該缺陷所需的彈性勢能。

---

## 📂 專案結構
本專案目前劃分為多個模組，對應不同的物理現象驗證：

```text
/V8
├── energydot_engine.py          # 核心宇宙演化引擎 (V8.4.0)
├── experiment/                  # 拓撲缺陷與質量定標實驗
├── gravitational_lensing/       # 引力透鏡實驗 (含偏折軌跡數據)
├── gravitational_wave/          # 雙波對比 (光波 vs 重力波)
└── speed_of_light/              # 示波器與光速測量

```

---

## 📊 驗證實驗進度

我們已經成功在數值模擬中觀測到多項經典物理現象，並獲得高精度的實驗數據：

| 實驗項目 | 關鍵指標 | 驗證狀態 |
| --- | --- | --- |
| **拓撲質量定標** | $M(R) = 1.1095R + 0.5114$, $R^2 = 0.9998$ | ✅ 成功 |
| **引力透鏡效應** | 測得偏折量 $\Delta Y \approx 4.73$ 格 | ✅ 成功 |
| **雙波對比** | 光波/重力波速比值 $c_g / c_e \approx 0.935$ | ✅ 成功 |

### 實驗軌跡：引力透鏡效應

下圖展示了光波在經過高斯引力井（空間剛度衰減區）時發生的測地線偏折現象：

---

## 📖 原理解析 (Quick Introduction)

**[中文]**
想像宇宙充滿了極小的「能量點」。它們沒有質量，僅在原地做零點振動。當這些點被極端擠壓並突破拓撲障礙時，會形成穩定的「團簇」——即我們觀測到的基本粒子。粒子會排開周圍的點，形成密度凹陷，其他粒子滾入其中，即湧現出「重力」。而光，則是這套網絡中傳播的推擠應力波。

**[English]**
Imagine the universe is filled with tiny "energy dots" undergoing zero-point vibrations. When forced past a topological threshold, they form stable clusters — our elementary particles. These clusters push away dots, creating "density dips" in the network; other clusters rolling into these dips manifests as **gravity**. **Light** is simply a push-wave propagating through this elastic lattice.

---

## 🗺️ 路線圖 (Roadmap)

* [x] **階段一**：$m \propto R$ 線性關係驗證。
* [x] **階段二**：V8.4.0 CUDA/CuPy 引擎開發與算子對齊。
* [ ] **階段三**：解決 Derrick's Theorem 導致的拓撲衰變，實現穩定孤子（Soliton）。
* [ ] **階段四**：電磁與引力的純幾何統一（Micropolar Elasticity）。

---

## 🤝 參與探索 (How You Can Help)

這是一個開放的科學探索專案，歡迎任何形式的「找碴」與建議：

1. **數值穩定性**：目前的引擎在高頻擾動下仍有數值色散，歡迎優化差分模板建議。
2. **孤子束縛**：針對對抗晶格坍縮，我們正在尋找更穩定的非線性勢能項。
3. **數據分析**：歡迎檢視我們各實驗模組的分析腳本。

---

## 📜 授權

MIT License - 隨意使用與改寫，期待您的貢獻。

