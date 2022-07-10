import numpy as np, matplotlib.pyplot as plt

def pend(y,t,b,c):
  return np.array([y[1], -b*y[1] - c*np.sin(y[0])])

def rungekutta4(f, y0, t, args=()):
  n = len(t)
  y = np.zeros((n, len(y0)))
  y[0] = y0
  for i in range(n - 1):
    h = t[i+1] - t[i]
    k1 = f(y[i], t[i], *args)
    k2 = f(y[i] + k1 * h / 2., t[i] + h / 2., *args)
    k3 = f(y[i] + k2 * h / 2., t[i] + h / 2., *args)
    k4 = f(y[i] + k3 * h, t[i] + h, *args)
    y[i+1] = y[i] + (h / 6.) * (k1 + 2*k2 + 2*k3 + k4)
  return y

if __name__ == '__main__':
  b = 0.25
  c = 5.0
  y0 = np.array([np.pi - 0.1, 0.0])

  t = np.linspace(0, 10, 101)
  
  t4 = np.linspace(0, 10, 21)
  sol4 = rungekutta4(pend, y0, t4, args=(b, c))

  t = np.linspace(0, 10, 101)
  sol = rungekutta4(pend, y0, t, args=(b, c))

  t2 = np.linspace(0, 10, 1001)
  sol2 = rungekutta4(pend, y0, t2, args=(b, c))

  plt.plot(t4, sol4[:, 0], label='with 21 points')
  plt.plot(t, sol[:, 0], label='with 101 points')
  plt.plot(t2, sol2[:, 0], label='with 1001 points')
  plt.legend(loc='best')
  plt.xlabel('t')
  plt.grid()
  plt.show()