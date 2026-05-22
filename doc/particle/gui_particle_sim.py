import tkinter as tk
from tkinter import ttk, messagebox
import cupy as cp
import matplotlib.pyplot as plt
import os
from lattice_core import EnergyLatticeSim3D

class ParticleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EnergyDot 終極物理實驗室控制台")
        self.root.geometry("380x280")
        
        # 1. 演化步數
        tk.Label(root, text="演化步數 (Steps):").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.steps_entry = tk.Entry(root)
        self.steps_entry.insert(0, "200")
        self.steps_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # 2. 實驗模式選擇
        tk.Label(root, text="選擇實驗項目:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.exp_combo = ttk.Combobox(root, values=[
            "實驗 A：雙電子同性排斥", 
            "實驗 A：正負電子異性吸引", 
            "實驗 B：電子自旋與角動量"
        ], state="readonly", width=25)
        self.exp_combo.current(0)
        self.exp_combo.grid(row=1, column=1, padx=10, pady=5)
        
        # 3. 自旋強度微調 (僅在實驗 B 有顯著效果)
        tk.Label(root, text="自旋強度 (僅實驗B):").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.spin_entry = tk.Entry(root)
        self.spin_entry.insert(0, "0.5")
        self.spin_entry.grid(row=2, column=1, padx=10, pady=5)
        
        # 說明文字區
        self.info_text = tk.Label(root, text="說明：選擇實驗後點擊下方按鈕開始模擬。", fg="gray")
        self.info_text.grid(row=3, column=0, columnspan=2, pady=10)
        
        # 4. 開始按鈕
        self.run_btn = tk.Button(root, text="🚀 啟動量子晶格模擬", command=self.run_experiment, bg="#008CBA", fg="white", font=("Arial", 11, "bold"))
        self.run_btn.grid(row=4, column=0, columnspan=2, padx=10, pady=10, ipadx=20, ipady=5)

    def run_experiment(self):
        try:
            steps = int(self.steps_entry.get())
            exp_type = self.exp_combo.get()
            spin_val = float(self.spin_entry.get())
            
            os.makedirs("data", exist_ok=True)
            sim = EnergyLatticeSim3D(size=128, mode="micro")
            
            exp_tag = ""
            
            # 根據選單配置實驗參數
            if exp_type == "實驗 A：雙電子同性排斥":
                exp_tag = "repulsion"
                # 注入兩個同為正符號（同荷）的電子
                sim.inject_real_electron((64, 50, 64), sign=1.0, spin=0.0)
                sim.inject_real_electron((64, 78, 64), sign=1.0, spin=0.0)
                
            elif exp_type == "實驗 A：正負電子異性吸引":
                exp_tag = "attraction"
                # 注入一正一負（異荷，正負電子湮滅前對撞態）
                sim.inject_real_electron((64, 50, 64), sign=1.0, spin=0.0)
                sim.inject_real_electron((64, 78, 64), sign=-1.0, spin=0.0)
                
            elif exp_type == "實驗 B：電子自旋與角動量":
                exp_tag = f"spin_{spin_val}"
                # 注入帶有切向扭轉剪切力的自旋電子
                sim.inject_real_electron((64, 50, 64), sign=1.0, spin=spin_val)
                sim.inject_real_electron((64, 78, 64), sign=1.0, spin=spin_val)

            # 開始演化
            for t in range(steps):
                sim.step()
                
            # 固化儲存數據（檔名自動包含實驗條件）
            file_base = f"data/exp_{exp_tag}_steps_{steps}"
            energy_density = cp.sum(sim.u**2, axis=0)
            
            plt.figure(figsize=(6,6))
            plt.imshow(cp.asnumpy(energy_density[64]), cmap='inferno')
            plt.title(f"{exp_type} ({steps} steps)")
            plt.axis('off')
            plt.savefig(f"{file_base}.png")
            plt.close()
            
            with open(f"{file_base}.txt", "w") as f:
                f.write(f"Experiment: {exp_type}\nSteps: {steps}\nSpin Value: {spin_val}\n")
                
            messagebox.showinfo("實驗固化成功", f"數據已成功儲存至：\n{file_base}.png")
            
        except Exception as e:
            messagebox.showerror("錯誤", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = ParticleGUI(root)
    root.mainloop()