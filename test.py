from scipy.integrate import ode
import matplotlib.pyplot as plt
import numpy as np
import random
import math

# === F U N C T I O N S ===

# Probability of tumbling
def p_tumble(C, W):
  # return 0.001 * max(-0.1 + C**2 - 0.9*W**2, 0.01)
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

random.seed(0)
kf = [0.61, 0.006, 0.37, 0.006, 0.006, 0.02]
kb = [4.7e-63, 0.006, 1.5e-41, None, None, None]
kd = 0.04

dt = 0.01
t_start = 0
t_end = 500
t = np.arange(t_start, t_end, dt)

cmap = plt.get_cmap('jet')
colors = cmap(np.linspace(0, 1.0, len(t)))
fig1, ax1 = plt.subplots()

# === I N I T ===

pos = [-100, -100]
alpha = random.uniform(0, 2*math.pi)
solution = [0., 0., 0.5, 0., 0., 1.]
sol = np.zeros(shape=(len(solution), len(t)))
sol[:, 0] = solution
x_pos = np.empty(len(t))
x_pos[0] = pos[0]
y_pos = np.empty(len(t))
y_pos[0] = pos[1]
prob = np.empty(len(t))
prob[0] = p_tumble(solution[2], solution[4])
dist = np.empty(len(t))
dist[0] = np.sqrt(pos[0]**2 + pos[1]**2)

k = 1

# === R U N ===

while k < len(t):

  tumble = p_tumble(solution[2], solution[4])
  if random.random() < tumble:
    # tumble
    alpha = random.uniform(0, 2*math.pi)
    dx = 0
    dy = 0
    ax1.scatter(pos[0], pos[1], marker='o')
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
    sol[:, k] = solution
    x_pos[k] = pos[0]
    y_pos[k] = pos[1]
    prob[k] = tumble
    dist[k] = np.sqrt(pos[0]**2 + pos[1]**2)

    k += 1

# ax1.plot(x_pos, y_pos, '-')

ax1.set_title("Single Bacterium's Tumbling Points")
ax1.set_xlim([-200, 200])
ax1.set_ylim([-200, 200])
plt.show()

# fig2, ax2 = plt.subplots()
# ax2.plot(t, sol[0,:], label='E')
# ax2.plot(t, sol[1,:], label='M')
# ax2.plot(t, sol[2,:], label='C')
# ax2.plot(t, sol[3,:], label='V')
# ax2.plot(t, sol[4,:], label='W')
# ax2.plot(t, sol[5,:], label='H')
# ax2.plot(t, prob*100, label='prob')
# ax2.plot(t, dist/-100, label='dist', alpha=0.25)
# ax2.set_xlabel("iteration")
# ax2.legend()
# fig2.text(.5, .05, 'Probability is multiplied by 100. Distance is divided by 100 and flipped.', ha='center')
# ax2.set_ylabel("[C] concentration")
# plt.show()
