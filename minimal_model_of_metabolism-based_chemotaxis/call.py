from scipy.integrate import ode
import matplotlib.pyplot as plt
import numpy as np
import min_model_fun
import random
import math

random.seed(814486220)

kf = [0.0183156, 0.606531, 0.0183156, 0.606531, 0.9905]
kb = [0.367879, 0, 0.367879, 0, 0]
k_degC = 0.0183156
k_degW = 0.0497871
alpha = random.uniform(0, 2*math.pi)

dt = 0.01
t_start = 0
t_end = 1e4
t = np.arange(t_start, t_end, dt)

pos = [0, 0]
elements = ['E', 'M', 'MC', 'C', 'W']
z0 = [0.05, 0.05, 0.05, 0.05, 0.05]

# === Outputs ===
# sol = np.empty((len(t), len(elements)))
# sol[0] = z0
sol_C = np.empty(len(t))
sol_C[0] = z0[3]

# === Plotting ===
fig1, ax1 = plt.subplots()
fig2, ax2 = plt.subplots()
cmap = plt.get_cmap('jet')
colors = cmap(np.linspace(0, 1.0, len(t)))
ax1.set_xlim([-100, 100])
ax1.set_ylim([-100, 100])

# === Initialise ===
solver = ode(min_model.ode_sys)
solver.set_integrator('rk45') # dop853
solver.set_f_params(kf, kb, k_degC, k_degW, pos)
solver.set_initial_value(z0, t_start)
ax1.scatter(pos[0], pos[1], color=colors[0], marker="o")
ax1.text(pos[0], pos[1], "start", fontdict={"c":colors[0]})

# fig1.show()
# fig1.canvas.draw()

k = 1

while k < len(t):

  if k % t_end == 0:
    temp = k/len(t) * 100
    print('%i %%' % temp)
    print(solver.y[3])
    ax1.scatter(pos[0], pos[1], color=colors[k], marker="o")
    # fig1.canvas.draw()

  if random.random() < min_model.p_tumble(solver.y[3]):
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

  if pos[0] < -100 or pos[1] < -100 or pos[0] > 100 or pos[1] > 100:
    # reverse and tumble
    pos[0] -= dx
    pos[1] -= dy
    alpha = random.uniform(0, 2*math.pi)
  else:
    solver.set_f_params(kf, kb, k_degC, k_degW, pos)
    solver.integrate(t[k])
    # sol[k] = solver.y
    sol_C[k] = solver.y[3]
    k += 1

print(pos)

ax1.scatter(pos[0], pos[1], color=colors[-1], marker="o")
ax1.text(pos[0], pos[1], "end", fontdict={"c":colors[-1]})
ax1.set_title("A bacterium's trajectory")
ax2.plot(t, sol_C)
ax2.set_title("Bacterium's [C] concentration over time")
ax2.set_xlabel("time")
ax2.set_ylabel("[C] concentration")
plt.show()