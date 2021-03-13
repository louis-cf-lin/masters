from scipy.integrate import odeint
import numpy as np

def p_tumble(C):
  return 1e-5 + (C*0.01)

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

def sys(y, t, kf, kb, k_degC, k_degW, pos):
  E, F, M, N, C, MC, NC, W, S, SE = y
  dydt = [
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
  return dydt

kf = [0.0183156, 0.606531, 0.0183156, 0.606531, 0.9905]
kb = [0.367879, 0, 0.367879, 0, 0]
k_degC = 0.0183156
k_degW = 0.0497871

pos = [0, 0]
elements = ['E', 'F', 'M', 'N', 'C', 'MC', 'NC', 'W', 'S', 'SE']
y0 = [D_in('E', pos), 0.05, D_in('M', pos), 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]

t = np.arange(0, 1, 0.01)

sol = odeint(sys, y0, t, args=(kf, kb, k_degC, k_degW, [0, 0]))

print(sol)

import matplotlib.pyplot as plt

cols = ['blue', 'brown', 'orange', 'pink', 'green', 'gray', 'red', 'olive', 'purple', 'cyan']

for i, elem in enumerate(elements):
  plt.plot(t, sol[:, i], 'tab:' + cols[i], label = elem)
plt.legend(loc='best')
plt.xlabel('t')
plt.grid()
plt.show()