# density_video.py
# Рисует графики плотности частиц, после по ним создаётся видео.

import os
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from dotenv import load_dotenv
import time

# Load variables from .env file
load_dotenv()

PARTICLE_NUM = int(os.getenv("PARTICLES_NUM", "0"))

X_FROM = -30
X_TO = 30
Y_FROM = -30
Y_TO = 30
VMAX = 100

plt.clf()  # Очищаем график для рисования плотности

print("Making video...")

L = np.load(f"./bin/trajectory_0.npy", mmap_mode='r').shape[0] // 9  # Количество шагов в траектории

fig, ax = plt.subplots()

H, xedges, yedges, img = ax.hist2d(
    [], [],
    bins=50,
    range=[[X_FROM, X_TO], [Y_FROM, Y_TO]],
    cmap='viridis',
    vmin=0,
    vmax=VMAX
)

cbar = fig.colorbar(img, ax=ax)
cbar.set_label("Particle Density")

start = time.time()

def update(step):
    ax.clear()
    
    ax.set_xlim(X_FROM, X_TO)
    ax.set_ylim(Y_FROM, Y_TO)
    
    # Собираем все координаты частиц на данном шаге
    x_coords = np.empty(PARTICLE_NUM, dtype=np.float32)
    y_coords = np.empty(PARTICLE_NUM, dtype=np.float32)
    
    for i in range(PARTICLE_NUM):
        traj = np.load(f"./bin/trajectory_{i}.npy", mmap_mode='r')
        row = traj[step]
        x_coords[i] = row[0]
        y_coords[i] = row[1]
    
    # Рисуем плотность частиц
    H, _, _, img = ax.hist2d(
        x_coords,
        y_coords,
        bins=50,
        range=[[X_FROM, X_TO], [Y_FROM, Y_TO]],
        cmap='viridis',
        vmin=0,
        vmax=VMAX
    )

    ax.set_title(f"Particle Density at Step {step}")
    
    now = time.time()
    remained_seconds = (L - step) * (now - start) / (step + 1)
    remained_minutes = int(remained_seconds // 60)
    remained_seconds_only = int(remained_seconds % 60)
    
    print(f"\r{step/L*100:.2f}% | Time elapsed: {int(now - start)//60}m {int(now - start)%60}s | Remaining time: {remained_minutes}m {remained_seconds_only}s", end="")

ani = animation.FuncAnimation(fig, update, frames=range(0, L))

ani.save("density.mp4", fps=30, writer="ffmpeg")

print("\r100.00%")
print("Video saved as density.mp4!")
print(f"Time taken: {time.time() - start:.2f} seconds")
print()
