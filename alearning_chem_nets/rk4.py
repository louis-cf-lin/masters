import numpy as np

def ode_RK4(f, X_0, dt, T):    
  N_t = int(round(T/dt))
  # Initial conditions
  usol = [X_0]
  u = np.copy(X_0)
  
  tt = np.linspace(0, N_t*dt, N_t + 1)
  # RK4
  for t in tt[:-1]:
    k1 = f(u, t)
    u1 = f(u + 0.5*dt* f(u, t), t + 0.5*dt)
    u2 = f(u + 0.5*dt*u1, t + 0.5*dt)
    u3 = f(u + dt*u2, t + dt)
    u = u + (1/6) * dt * ( f(u, t) + 2*u1 + 2*u2 + u3)
    usol.append(u)
  return usol, tt

def rk4(f, y0, t, args=()):
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

def demo_exp():
  import matplotlib.pyplot as plt
  
  def f(u, t):
    return np.asarray([u])

  u, t = ode_RK4(f, np.array([1]) , 0.1, 1.5)
  
  plt.plot(t, u, "b*", t, np.exp(t), "r-")
  plt.show()
    
def demo_osci():
  import matplotlib.pyplot as plt
  
  def f(u, t, omega=2):
    u, v = u 
    return np.asarray([v, -omega**2*u])
  
  u, t = ode_RK4(f, np.array([2,0]), 0.1, 2)
  
  u1 = [a[0] for a in u]
  
  for i in [1]:
    plt.plot(t, u1, "b*")
  plt.show()

demo_exp()