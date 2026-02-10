# Open trajectories files and visualize them

import os
import numpy as np
from matplotlib import pyplot as plt
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

Y_FROM = -3
Y_TO = 3
X_FROM = -1
X_TO = 8

PARTICLE_NUM = int(os.getenv("PARTICLES_NUM", "0"))
U_FUNCTION = int(os.getenv("U_FUNCTION", "1"))

print(f'Visualizing {PARTICLE_NUM} particles trajectories...')

fig, ax = plt.subplots(figsize=(14, 10))

# Create wind velocity field
x_wind = np.linspace(X_FROM, X_TO, 15)
y_wind = np.linspace(Y_FROM, Y_TO, 15)
X_wind, Y_wind = np.meshgrid(x_wind, y_wind)

# WIND VELOCITY FIELDS

# CONSTANT WIND FIELD
U_wind = 10.0 * np.ones_like(X_wind)
V_wind = 5.0 * np.ones_like(Y_wind)

if U_FUNCTION == 2:
    # VARIABLE WIND FIELD #1
    U_wind = 10.0 + Y_wind * np.sin(Y_wind * np.pi) + np.exp(-0.1 * X_wind) - 5
    V_wind = 5.0 + 0.3 * X_wind * np.sin(Y_wind * np.pi) + 3

elif U_FUNCTION == 3:
    # VARIABLE WIND FIELD #2
    U_wind = X_wind * np.cos(Y_wind * np.pi / 2) +  Y_wind + 5
    V_wind = 10*np.sin(Y_wind * np.pi / 2)

ax.streamplot(X_wind, Y_wind, U_wind, V_wind, color='gray', density=5, linewidth=1, arrowsize=1.5)

# Plot particle trajectories
for i in range(PARTICLE_NUM):
    try:
        trajectory = np.loadtxt(f'./trajectories/trajectory_{i}.txt')
        x = trajectory[:, 0]
        y = trajectory[:, 1]
        
        plt.plot(x, y, linewidth=1.5, alpha=0.7, label=f'Particle {i}' if i < 5 else '')
    except FileNotFoundError:
        print(f'Warning: trajectory_{i}.txt not found')
        continue

# Set axis limits and labels
ax.set_xlim(X_FROM, X_TO)
ax.set_ylim(Y_FROM, Y_TO)
ax.set_xlabel('X (m)', fontsize=12)
ax.set_ylabel('Y (m)', fontsize=12)
ax.set_title(f'Particle Trajectories in Variable Wind Field', fontsize=14)

ax.grid(True, alpha=0.3)

# Add wind velocity annotation
if U_FUNCTION == 1:
    ax.text(0.02, 0.98, f'Constant wind field (m/s):\nUx = 10\nUy = 5', 
        transform=ax.transAxes, fontsize=11, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
elif U_FUNCTION == 2:
    ax.text(0.02, 0.98, f'Variable wind field (m/s):\nUx(x,y) = 5 + y*sin(y*pi) + exp(-0.1*x)\nUy(x,y) = 8 + 0.3*x*sin(y*pi)', 
        transform=ax.transAxes, fontsize=11, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
elif U_FUNCTION == 3:
    ax.text(0.02, 0.98, f'Variable wind field (m/s):\nUx(x,y) = x*cos(y*pi/2) + y + 5\nUy(x,y) = 10*sin(y*pi/2)', 
            transform=ax.transAxes, fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Show only first few particles in legend
handles, labels = ax.get_legend_handles_labels()
if len(handles) > 0:
    ax.legend(loc='upper right', fontsize=10)

plt.tight_layout()

plt.savefig(f'wind_field_{U_FUNCTION}_particles_{PARTICLE_NUM}.png', dpi=300)
plt.show()