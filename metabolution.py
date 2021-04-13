from scipy.integrate import ode
import matplotlib.pyplot as plt
import numpy as np
import random
import math

# === F U N C T I O N S ===

# Probability of tumbling
def p_tumble(C, W):
  return 0.01 * max(-0.1 + C**2 - 0.9*W**2, 0.01)

# Rate of transport of chemicals from environment into bacteria
def k_d(pos, element):
  if element == 'M' or element == 'E':
    left = kd * np.exp(-((pos[0] + 75)**2 + pos[1]**2) / 2000)
    right = kd * np.exp(-((pos[0] - 75)**2 + pos[1]**2) / 2000)
    return left + right
  elif (element == 'S'):
    if np.sqrt((pos[0] + 75)**2 + (pos[1])**2) < 0.5:
      return kd
    else:
      return 0
  elif (element == 'F' or element == 'N'):
    return kd * np.exp(-(pos[0]**2 + pos[1]**2) / 2000)

# System of ODE's
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

# Single bacterium run
def single_run(init_pos):
  pos = init_pos
  alpha = random.uniform(0, 2*math.pi)
  solution = [0., 0., 0.5, 0., 0., 1., 0., 0., 0.]
  sol = np.zeros(shape=(len(solution), len(t)))
  sol[:, 0] = solution
  x_pos = np.empty(len(t))
  x_pos[0] = pos[0]
  y_pos = np.empty(len(t))
  y_pos[0] = pos[1]
  prob = np.empty(len(t))
  prob[0] = p_tumble(solution[2], solution[4])

  if plot_tumbling_points:
    fig1, ax1 = plt.subplots()
    tumble_x = []
    tumble_y = []
    tumble_prob = []

  k = 1

  # === R U N ===

  while k < len(t):

    tumble = p_tumble(solution[2], solution[4])
    if random.random() < tumble:
      # tumble
      alpha = random.uniform(0, 2*math.pi)
      dx = 0
      dy = 0
      if plot_tumbling_points:
        tumble_x.append(pos[0])
        tumble_y.append(pos[1])
        tumble_prob.append(tumble)
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
      solution = euler(solution, dt, kf, kb, pos)
      sol[:, k] = solution
      x_pos[k] = pos[0]
      y_pos[k] = pos[1]
      prob[k] = tumble
      k += 1

  if plot_tumbling_points:
    sc = ax1.scatter(tumble_x, tumble_y, marker='o', c=tumble_prob, cmap='plasma', edgecolor='none')
    ax1.set_title("Single Bacterium Tumbling Points")
    ax1.set_xlim([-100, 100])
    ax1.set_ylim([-100, 100])
    fig1.colorbar(sc)

  if plot_single_trajectory:
    _, ax2 = plt.subplots()
    ax2.set_title("Single Bacterium Trajectory")
    ax2.set_xlim([-100, 100])
    ax2.set_ylim([-100, 100])
    ax2.add_patch(plt.Circle((-75, 0), 0.5, color='red', fill=False))
    ax2.scatter(x_pos, y_pos, s=0.1, marker='.', c=np.linspace(1,10,len(t)), cmap='jet')

  if plot_chems:
    _, ax3 = plt.subplots()
    iteration = t/dt
    ax3.plot(iteration, sol[0,:], label='E / M')
    ax3.plot(iteration, sol[2,:], label='C')
    ax3.plot(iteration, sol[3,:], label='V')
    ax3.plot(iteration, sol[4,:], label='W')
    # ax3.plot(iteration, sol[5,:], label='H')
    ax3.plot(iteration, sol[6,:], label='F / N')
    ax3.plot(iteration, sol[8,:], label='S')
    ax3.set_xlabel("iteration")
    ax3.legend()

  if plot_all:
    fig4, ax4 = plt.subplots()
    iteration = t/dt
    ax4.plot(iteration, sol[2,:], label='C')
    ax4.plot(iteration, sol[4,:], label='W')
    ax4.plot(iteration, prob*100, label='prob')
    ax4.plot(iteration, ( np.sqrt( (x_pos+75)**2 + (y_pos)**2 ) )/-100, label='dist from (-75,0)')
    ax4.plot(iteration, ( np.sqrt( (x_pos-75)**2 + (y_pos)**2 ) )/-100, label='dist from (+75,0)')
    ax4.plot(iteration, ( np.sqrt( (x_pos)**2 + (y_pos)**2 ) )/-100, label='dist from (0,0)')
    fig4.text(.5, 0.01, 'Probability is multiplied by 100.', ha='center')
    fig4.subplots_adjust(bottom=0.2)
    ax4.set_xlabel("iteration")
    ax4.legend()
  
  print(sol[-1,-1])
  plt.show()

# Population run

def pop_run():
  if plot_population:
    _, ax5 = plt.subplots()

  for i in range(10):
    for j in range(10):
      print(i, j, sep='')
      # === I N I T ===
      pos = [i*20 - 90, j*20 - 90]
      alpha = random.uniform(0, 2*math.pi)
      solution = [0., 0., 0.5, 0., 0., 1., 0., 0., 0.]
      k = 1
      # === R U N ===
      while k < len(t):
        tumble = p_tumble(solution[2], solution[4])

        if random.random() < tumble:
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
          solution = euler(solution, dt, kf, kb, pos)
          k += 1

      if plot_population:
        if solution[-1] > 0:
          print('got one!')
          ax5.scatter(pos[0], pos[1], marker='o', color='blue', alpha=0.25)
        else:
          ax5.scatter(pos[0], pos[1], marker='x', color='red', alpha=0.25)

  if plot_population:
    # ax5.set_title("Single Bacterium Tumbling Points")
    ax5.set_xlim([-100, 100])
    ax5.set_ylim([-100, 100])
  
  plt.show()


# === H Y P E R P A R A M E T E R S ===

plot_tumbling_points = True
plot_single_trajectory = True
plot_chems = True
plot_all = True
plot_population = True

single = True

# === C O N S T A N T S ===

random.seed(0)
kf = [0.61, 0.006, 0.37, 0.006, 0.006, 0.02, 0.0001, 0.99]
kb = [4.7e-63, 0.006, 1.5e-41, None, None, None, None, 9.6e-67]
kd = 0.04

dt = 0.01
t_start = 0
t_end = 900
t = np.arange(t_start, t_end, dt)

cmap = plt.get_cmap('jet')
colors = cmap(np.linspace(0, 1.0, len(t)))

# === S I N G L E ===

if single:
  single_run([-76, 2])
else:
  pop_run()
