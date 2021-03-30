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
def k_d(pos, element):
  if element == 'M' or element == 'E':
    left = kd * np.exp(-((pos[0]-75)**2 + pos[1]**2) / 2000)
    right = kd * np.exp(-((pos[0]+75)**2 + pos[1]**2) / 2000)
    return left + right
  elif (element == 'S'):
    if np.sqrt((pos[0] + 75)**2 + (pos[1])**2) < 0.5:
      return kd
    else:
      return 0
  elif (element == 'F' or element == 'N'):
    return kd * np.exp(-(pos[0]**2 + pos[1]**2) / 2000)

def euler(y0, h, kf, kb, pos):
  E, M, C, V, W, H, F, N, S = y0
  k_f = [kf[0]*E*M*C, kf[1]*C*H, kf[2]*C*H*V**2/2, kf[3]*C*V**2/2, kf[4]*C*W**2/2, kf[5]*H, kf[6]*S, kf[7]*C*F*N*S]
  k_b = [kb[0]*C**2*V**2/4, kb[1]*H*W, kb[2]*C*H**2*W**2/4, None, None, None, None, kb[7]*C**2*V**2*S**2/6]
  f = [
    -k_f[0] + k_b[0] + k_d(pos, 'E'), # E
    -k_f[0] + k_b[0] + k_d(pos, 'M'), # M
    -k_f[0] + k_b[0] - 2*k_b[0] + 2*k_f[0] - k_f[1] + k_b[1] - k_f[3] - k_f[4] - k_f[7] + k_b[7] - 2*k_b[7] + 2*k_f[7], # C
    -2*k_b[0] + 2*k_f[0] - 2*k_f[2] + 2*k_b[2] - 2*k_f[3] - 2*k_b[7] + 2*k_f[7], # V
    -k_b[1] + k_f[1] - 2*k_b[2] + 2*k_f[2] - 2*k_f[4], # W
    -k_f[2] + k_b[2] - 2*k_b[2] + 2*k_f[2] - k_f[5], # H
    -k_f[7] + k_b[7] + k_d(pos, 'F'), # F
    -k_f[7] + k_b[7] + k_d(pos, 'N'), # N
    -k_f[6] - k_f[7] + k_b[7] - 2*k_b[7] + 2*k_f[7] + k_d(pos, 'S') # S
  ]
  return y0 + np.multiply(f, h)

# === C O N S T A N T S ===

random.seed(814486224)
kf = [0.61, 0.006, 0.37, 0.006, 0.006, 0.02, 0.0001, 0.99]
kb = [4.7e-63, 0.006, 1.5e-41, None, None, None, None, 9.6e-67]
kd = 0.04

dt = 0.01
t_start = 0
t_end = 500
t = np.arange(t_start, t_end, dt)

fig1, ax1 = plt.subplots()

for i in range(10):
  for j in range(10):

    print(i, j, sep='')

    if i == 8 and j == 1:
      print('stop right there')

    # === I N I T ===

    pos = [i*40 - 180, j*40 - 180]
    alpha = random.uniform(0, 2*math.pi)
    solution = [0., 0., 0.5, 0., 0., 1., 0., 0., 0.]

    # sol = np.empty((len(t), len(elements)))
    # sol[0] = z0
    # sol_C = np.empty(len(t))
    # sol_C[0] = z0[2]

    k = 0

    # === R U N ===

    while k < len(t):

      # if k % t_end == 0:
      #   temp = k/len(t) * 100
      #   print('%i %%' % temp)
      #   print(solver.y[2])
      #   ax1.scatter(pos[0], pos[1], color=colors[k], marker="o")

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

    ax1.scatter(pos[0], pos[1])

# ax1.scatter(pos[0], pos[1], color=colors[-1], marker="o")
# ax1.text(pos[0], pos[1], "end", fontdict={"c":colors[-1]})

ax1.set_title("A bacterium's trajectory")
ax1.set_xlim([-200, 200])
ax1.set_ylim([-200, 200])
plt.show()