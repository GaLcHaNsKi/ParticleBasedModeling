# Open trajectories files and visualize them

import os
import numpy as np
from matplotlib import pyplot as plt
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

Y_FROM = -50
Y_TO = 50
X_FROM = -50
X_TO = 50

PARTICLE_NUM = int(os.getenv("PARTICLES_NUM", "0"))

print(f'Visualizing {PARTICLE_NUM} particles trajectories...')

for i in range(PARTICLE_NUM):
    trajectory = np.loadtxt(f'./trajectories/trajectory_{i}.txt')
    x = trajectory[:, 0]
    y = trajectory[:, 1]
    plt.plot(x, y, label=f'Particle {i}')

# plt.xlim(X_FROM, X_TO)
# plt.ylim(Y_FROM, Y_TO)
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Particle Trajectories')

plt.grid()
plt.show()