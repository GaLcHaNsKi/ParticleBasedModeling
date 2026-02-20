# txt_to_bin.py
# Конвертирует .txt файлы с траекториями в .npy для более быстрой загрузки в density_video.py.

import numpy as np
import os
import time
from dotenv import load_dotenv

load_dotenv()

PARTICLE_NUM = int(os.getenv("PARTICLES_NUM", "0"))

os.makedirs("bin", exist_ok=True)

start = time.time()

print("Converting .txt data to .npy format...")

for i in range(PARTICLE_NUM):
    data = np.loadtxt(f'./trajectories/trajectory_{i}.txt')
    np.save(f'./bin/trajectory_{i}.npy', data)
    
    seconds = time.time() - start
    mins = int(seconds // 60)
    s = int(seconds % 60)
    
    remained_seconds = (PARTICLE_NUM - i - 1) * (seconds / (i + 1))
    remained_minutes = int(remained_seconds // 60)
    remained_seconds_only = int(remained_seconds % 60)
    
    print(f"\r{(i + 1) / PARTICLE_NUM * 100:.2f}% | Time: {mins}m {s}s | Remained time: {remained_minutes}m {remained_seconds_only}s", end="")

print("\r100.00%")
print("Done.")

seconds = time.time() - start
mins = int(seconds // 60)
s = int(seconds % 60)

print(f"Time taken: {mins}m {s}s")