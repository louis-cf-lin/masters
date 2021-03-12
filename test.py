from scipy.integrate import odeint
import numpy as np

def sys(y, t, b, c):
  E, F, M, N, C, MC, NC, W, S, SE = y
  dydt = [
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0
  ]
  return dydt

b = 0.25
c = 5.0

y0 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

t = np.arange(0, 1, 0.01)

sol = odeint(sys, y0, t, args=(b, c))

print(sol)