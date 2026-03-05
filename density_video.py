# density_video.py
# Читает готовые 60x60 матрицы плотности и делает видео

import os
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import time

X_FROM = -30
X_TO = 30
Y_FROM = -30
Y_TO = 30

GRID_SIZE = 60
STEPS = 5000 // 5
VMAX = int(input("Enter the maximum density value: "))
FPS = 30

print("Making video...")

fig, ax = plt.subplots()

density = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float32)

img = ax.imshow(
    density,
    origin="lower",
    extent=[X_FROM, X_TO, Y_FROM, Y_TO],
    cmap="viridis",
    vmin=0,
    vmax=VMAX,
    interpolation="nearest"
)

cbar = fig.colorbar(img, ax=ax)
cbar.set_label("Particle Density")

ax.set_xlim(X_FROM, X_TO)
ax.set_ylim(Y_FROM, Y_TO)

start = time.time()


def update(step):
    filename = f"./density/density_{step}.txt"
    density = np.loadtxt(filename).reshape((GRID_SIZE, GRID_SIZE))

    img.set_data(density)

    ax.set_title(f"Particle Density at Step {step}")

    now = time.time()
    elapsed = now - start

    percent = step / STEPS * 100
    remaining = (STEPS - step) * elapsed / (step + 1)

    rm = int(remaining // 60)
    rs = int(remaining % 60)

    em = int(elapsed // 60)
    es = int(elapsed % 60)

    print(
        f"\r{percent:.2f}% | "
        f"Elapsed: {em}m {es}s | "
        f"Remaining: {rm}m {rs}s",
        end=""
    )

ani = animation.FuncAnimation(
    fig,
    update,
    frames=range(STEPS)
)

ani.save("density.mp4", fps=FPS, writer="ffmpeg")

print("\r100.00%")
print("Video saved as density.mp4!")
print(f"Time taken: {time.time() - start:.2f} seconds")
print()
