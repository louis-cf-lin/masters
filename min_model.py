from scipy.integrate import ode
import numpy as np
import matplotlib.pyplot as plt
import random
import math

def p_tumble(C):
  return 1e-5 + (C*0.01)

def D_in(element, pos):
  if element == 'M':
    offsetX = 0
    offsetY = 0
  elif element == 'E':
    offsetX = 0
    offsetY = 0
  else:
    offsetX = 0
    offsetY = 0
  
  dist = np.sqrt((pos[0]-offsetX)*(pos[0]-offsetX) + (pos[1]-offsetY)*(pos[1]-offsetY))
  return 0.2 * np.exp(-dist / 2000)

def sys(t, z, kf, kb, k_degC, k_degW, pos):
  E, F, M, N, C, MC, NC, W, S, SE = z
  f = [
    -kf[1]*MC*E + kb[1]*C**2*W/2 + D_in('E', pos) - kf[4]*S*E + kf[4]*SE,
    -kf[0]*M*C + kb[0]*MC + D_in('M', pos),
    -kb[0]*M*C + kf[0]*M*C - kf[1]*E*MC + kb[1]*C**2*W/2,
    -kf[3]*NC*F + kb[3]*C**2*W/2 + D_in('F', pos),
    kf[2]*N*C + kb[2]*NC + D_in('N', pos),
    -kb[2]*NC + kf[2]*N*C - kf[3]*F*NC + kb[3]*C**2*W/2,
    -kf[0]*M*C + kb[0]*MC - 2*kb[1]*C**2*W/2 + 2*kf[1]*E*MC - kf[2]*N*C + kb[2]*NC - 2*kb[3]*C**2*W/2 + 2*kf[3]*F*NC - k_degC*C,
    -kb[1]*C**2*W/2 + kf[1]*E*MC - kb[3]*C**2*W/2 + kf[3]*F*NC - k_degW*W,
    -kf[4]*S*E + kb[4]*SE,
    -kb[4]*SE + kf[4]*S*E
  ]
  return f

kf = [0.0183156, 0.606531, 0.0183156, 0.606531, 0.9905]
kb = [0.367879, 0, 0.367879, 0, 0]
k_degC = 0.0183156
k_degW = 0.0497871

pos = [50, 50]
elements = ['E', 'F', 'M', 'N', 'C', 'MC', 'NC', 'W', 'S', 'SE']
z0 = [D_in('E', pos), 0.05, D_in('M', pos), 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]

dt = 0.01
t_start = 0
t_end = 1000

solver = ode(sys)
solver.set_integrator('dop853')
solver.set_f_params(kf, kb, k_degC, k_degW, pos)
solver.set_initial_value(z0, t_start)

t = np.arange(t_start, t_end, dt)
sol = np.empty((len(t), len(elements)))
sol[0] = z0

fig, ax = plt.subplots()
all_pos = []


alpha = random.uniform(0, 2*math.pi)
k = 1
# while solver.successful() and solver.t < t[-1]:
while k < t_end:

  # ax.scatter(pos[0], pos[1], c="r", marker="o")
  
  if random.random() < p_tumble(solver.y[5]):
    dx = 0
    dy = 0
  else:
    alpha = random.uniform(0, 2*math.pi)
    dx = 1 * math.cos(alpha)
    dy = 1 * math.sin(alpha)

  pos[0] += dx
  pos[1] += dy

  solver.set_f_params(kf, kb, k_degC, k_degW, pos)
  solver.integrate(t[k])
  sol[k] = solver.y

  k += 1

print(pos)
# plt.show()

# cols = ['blue', 'brown', 'orange', 'pink', 'green', 'gray', 'red', 'olive', 'purple', 'cyan']
# for i, elem in enumerate(elements):
#   plt.plot(t, sol[:, i], 'tab:' + cols[i], label = elem)
# plt.legend(loc='best')
# plt.xlabel('t')
# plt.grid()
# plt.show()


# env_x, env_y = np.meshgrid(np.arange(-100,101), np.arange(-100,101)) 
# dst = np.sqrt((env_x - 100)*(env_x - 100) + env_y*env_y) 

# env = np.exp(-dst / 2000)

# plt.contourf(env_x, env_y, env, cmap='Blues')
# plt.colorbar()
# plt.show()