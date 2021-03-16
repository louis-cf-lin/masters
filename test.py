from scipy.integrate import ode
import numpy as np
import matplotlib.pyplot as plt
import random
import math

# Probability of tumbling
def p_tumble(C):
  return 1e-5 + (C*0.01)

# Rate of transport of chemicals from environment into bacteria
def D_in(element, pos):
  if element == 'M':
    offsetX = 100
    offsetY = 0
  elif element == 'E':
    offsetX = 100
    offsetY = 0
  else:
    offsetX = 0
    offsetY = 0
  dist = np.sqrt((pos[0]-offsetX)*(pos[0]-offsetX) + (pos[1]-offsetY)*(pos[1]-offsetY))
  return 0.2 * np.exp(-dist / 2000)

# System of ODE's
def sys(t, z, kf, kb, k_degC, k_degW, pos):
  E, M, MC, C, W = z
  f = [
    -kf[1]*MC*E + kb[1]*C**2*W/2 + D_in('E', pos),
    -kf[0]*M*C + kb[0]*MC + D_in('M', pos),
    -kb[0]*MC + kf[0]*M*C - kf[1]*E*MC + kb[1]*C**2*W/2,
    -kf[0]*M*C + kb[0]*MC - 2*kb[1]*C**2*W/2 + 2*kf[1]*E*MC - 2*kb[3]*C**2*W/2 - k_degC*C,
    -kb[1]*C**2*W/2 + kf[1]*E*MC - kb[3]*C**2*W/2 - k_degW*W
  ]
  return f

kf = [0.0183156, 0.606531, 0.0183156, 0.606531, 0.9905]
kb = [0.367879, 0, 0.367879, 0, 0]
k_degC = 0.0183156
k_degW = 0.0497871

pos = [0, 0]
elements = ['E', 'M', 'MC', 'C', 'W']
z0 = [0.05, 0.05, 0.05, 0.05, 0.05]

dt = 0.01
t_start = 0
t_end = 2.5e5

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
while k < len(t):

  if k % t_end == 0:
    temp = k/len(t) * 100
    print('%i %%' % temp)
    print(pos)
    print(solver.y[3])
  
  if random.random() < p_tumble(solver.y[3]):
    alpha = random.uniform(0, 2*math.pi)
    dx = 0
    dy = 0
  else:
    dx = 0.05 * math.cos(alpha)
    dy = 0.05 * math.sin(alpha)

  pos[0] += dx
  pos[1] += dy

  if pos[0] < -100 or pos[1] < -100 or pos[0] > 100 or pos[1] > 100:
    pos[0] -= dx
    pos[1] -= dy
  else:
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