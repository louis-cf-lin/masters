from scipy.integrate import ode
import matplotlib.pyplot as plt
import numpy as np
import random
import math

# === F U N C T I O N S ===

# Probability of tumbling
def p_tumble(C, W):
  return 0.001 * max(-0.1 + C**2 - 0.9*W**2, 0.01)

# Rate of transport of chemicals from environment into bacteria
def k_d(pos):
  return kd * np.exp(-(pos[0]**2 + pos[1]**2) / 2000)

# System of ODE's
def euler(y0, h, kf, kb, pos):
  E, M, C, V, W, H = y0
  k_f = [kf[0]*E*M*C, kf[1]*C*H, kf[2]*C*H*V**2/2, kf[3]*C*V**2/2, kf[4]*C*W**2/2, kf[5]*H]
  k_b = [kb[0]*C**2*V**2/4, kb[1]*H*W, kb[2]*C*H**2*W**2/4, None, None, None]
  f = [
    -k_f[0] + k_b[0] + k_d(pos), # E
    -k_f[0] + k_b[0] + k_d(pos), # M
    -k_f[0] + k_b[0] - 2*k_b[0] + 2*k_f[0] - k_f[1] + k_b[1] - k_f[3] - k_f[4], # C
    -2*k_b[0] + 2*k_f[0] - 2*k_f[2] + 2*k_b[2] - 2*k_f[3], # V
    -k_b[1] + k_f[1] - 2*k_b[2] + 2*k_f[2] - 2*k_f[4], # W
    -k_f[2] + k_b[2] - 2*k_b[2] + 2*k_f[2] - k_f[5] # H
  ]
  return y0 + np.multiply(f, h)

# === C O N S T A N T S ===

random.seed(814486224)
kf = [0.61, 0.006, 0.37, 0.006, 0.006, 0.02]
kb = [4.7e-63, 0.006, 1.5e-41, None, None, None]
kd = 0.04

dt = 0.01
t_start = 0
t_end = 500
t = np.arange(t_start, t_end, dt)

fig1, ax1 = plt.subplots()

for i in range(10):
  for j in range(10):

    print(i, j, sep='')

    # === I N I T ===

    pos = [i*40 - 180, j*40 - 180]
    alpha = random.uniform(0, 2*math.pi)
    solution = [0., 0., 0.5, 0., 0., 1.]

    k = 0

    # === R U N ===

    while k < len(t):

      if random.random() < p_tumble(solution[2], solution[4]):
        # tumble
        alpha = random.uniform(0, 2*math.pi)
        dx = 0
        dy = 0
      else:
        # run
        dx = 0.05 * math.cos(alpha)
        dy = 0.05 * math.sin(alpha)

      pos[0] += dx
      pos[1] += dy

      if pos[0] < -200 or pos[1] < -200 or pos[0] > 200 or pos[1] > 200:
        # reverse and tumble
        pos[0] -= dx
        pos[1] -= dy
        alpha = random.uniform(0, 2*math.pi)
      else:
        solution = euler(solution, dt, kf, kb, pos)
        k += 1

    ax1.scatter(pos[0], pos[1], marker="o")


ax1.set_title("Final positions")
ax1.set_xlim([-200, 200])
ax1.set_ylim([-200, 200])
plt.show()