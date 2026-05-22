from lattice_core import EnergyLatticeSim3D
import cupy as cp
import matplotlib.pyplot as plt
import imageio.v2 as imageio
import os

# 初始化
sim = EnergyLatticeSim3D(size=128, mode="micro")
sim.add_energy_cluster((64, 50, 64), radius=5.0, density=1.0)
sim.add_energy_cluster((64, 78, 64), radius=5.0, density=1.0)

filenames = []
print("🚀 正在渲染演化幀...")

# 演化與存檔
for t in range(200):
    sim.step()
    if t % 5 == 0:
        energy_density = cp.sum(sim.u**2, axis=0)
        
        # 存成臨時 PNG
        filename = f"temp_frame_{t:04d}.png"
        plt.imshow(cp.asnumpy(energy_density[64]), cmap='inferno')
        plt.axis('off') # 隱藏座標軸讓畫面乾淨
        plt.savefig(filename)
        plt.close() # 關閉畫布避免記憶體洩漏
        filenames.append(filename)

# 製作 GIF
print("🎬 正在合成 GIF...")
with imageio.get_writer('soliton_evolution.gif', mode='I', duration=0.1) as writer:
    for filename in filenames:
        image = imageio.imread(filename)
        writer.append_data(image)

# 刪除臨時檔案
for filename in filenames:
    os.remove(filename)

print("✅ GIF 合成完畢！")