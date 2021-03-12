# import numpy as np
# import matplotlib.pyplot as plt
import random as random
import math as math
from scipy.integrate import ode

# metabolic product
C = 0.5
# waste ?
W = 0
# some reactant ?
H = 1

# activation energy
A = 0
# combined reactant energy level
R = 0
# combined product energy level
P = 0

# rate constant of diffusion
k_d = 0.04
# forward reaction (exergonic)
# k_f = np.exp(A)
k_f = [0.61, 0.006, 0.37, 0.006, 0.02, 0.0001, 0.99]
# backward reaction (endergonic)
# k_b = np.exp(A + R - P)
k_b = [4.7e-63, 0.006, 1.5e-41, None, None, None, None, 9.6e-67]

# orientation
alpha = random.uniform(0,2*math.pi)

d_x = 0.05 * math.cos(alpha)
d_y = 0.05 * math.sin(alpha)

# probability of tumbling
p_tumble = 0.001 * max(-0.1 + C**2 - 0.9*W**2, 0.01)


y0, t0 = [1.0j, 2.0], 0

def d_E(E, M, C, V, k_d):
  return -k_f[0] + (k_b[0] * C**2 * V**2)/4 + k_d

def d_M(E, M, C, V, k_d):
  return -k_f[0] + (k_b[0] * C**2 * V**2)/4 + k_d

def d_C(E, M, C, V, S, F, N):
  return -k_f[0]*E*M*C + k_b[0]*C**2*V**2/4 - 2*k_b[0]*C**2*V**2/4 + 2*k_f[0]*E*M*C - k_f[1]*C*H + k_b[1]*H*W - k_f[3]*C*V**2/2 - k_f[4]*C*W**2/2 - k_f[7]*C*F*N*S + k_b[7]*C**2*V**2*S**2/6 - 2*k_b[7]*C**2*V**2*S**2/6 + 2*k_f[7]*C*F*N*S

def d_V(E, M, C, V, S, F, N, H):
  return -2*k_b[0]*C**2*V**2/4 + 2*k_f[0]*E*M*C - 2*k_f[2]*C*H*V**2/2 + 2*k_b[2]*C*H**2*W**2/4 - 2*k_f[3]*C*V**2/2 - 2*k_b[7]*C**2*V**2*S**2/6 + 2*k_f[7]*C*F*N*S

def d_W(E, M, C, V, S, F, N, H):
  return -k_b[1]*H*W + k_f[1]*C*H - 2*k_b[2]*C*H**2*W**2/4 + 2*k_f[2]*C*H*V**2/2 - 2*k_f[4]**C*W**2/2

def d_H(E, M, C, V, S, F, N, H):
  return -k_f[2]*C*H*V**2/2 + k_b[2]*C*H**2*W**2/4 - 2*k_b[2]*C*H**2*W**2/4 + 2*k_f[2]*C*H*V**2/2 - k_f[5]*H

def d_F(C, V, S, F, N, k_d):
  return -k_f[7]*C*F*N*S + k_b[7]*C**2*V**2*S**2/6 + k_d

def d_N(C, F, N, S, V, k_d):
  return -k_f[7]*C*F*N*S + k_b[7]*C**2*V**2*S**2/6 + k_d

def d_S(S, C, F, N, V, k_d):
  return -k_f[6]*S - k_f[7]*C*F*N*S + k_b[7]*C**2*V**2*S**2/6 - 2*k_b[7]*C**2*V**2*S**2/6 + 2*k_f[7]*C*F*N*S + k_d

r = ode(d_E, d_M, d_C, d_V, d_W, d_H, d_F, d_N, d_S).set_integrator('zvode', method='bdf')
r.set_initial_value(y0, t0).set_f_params(2.0).set_jac_params(2.0)
t1 = 10
dt = 1

# n = 100
# threshold = 0.95

# mesh_x, mesh_y = np.meshgrid(np.linspace(-1,1,n), np.linspace(-1,1,n)) 
# dst = np.sqrt(mesh_x*mesh_x + mesh_y*mesh_y) 
# sigma = 1
# muu = 0.000
# gauss = np.exp(-((dst-muu)**2 / (2.0 * sigma**2))) 
# scaled = np.sqrt(np.log(threshold) * -(2 * sigma**2))

# x = [random.uniform(-1,1)]
# y = [random.uniform(-1,1)]

# d_x = 0
# d_y = 0
# d_theta = 0

# f_val = np.exp(-((np.sqrt(x[-1]*x[-1] + y[-1]*y[-1]) - muu)**2 / (2.0 * sigma**2)))

# while (f_val <= threshold):
#   if (x[-1] < -1 or x[-1] > 1 or y[-1] < -1 or y[-1] > 1):
#     x.pop()
#     y.pop()
#   d_theta = random.uniform(0, 360)
#   d_x = 0.1
#   x.append(d_x*math.cos(d_theta) + x[-1])
#   y.append(d_x*math.sin(d_theta) + y[-1])
#   f_val = np.exp(-((np.sqrt(x[-1]*x[-1] + y[-1]*y[-1]) - muu)**2 / (2.0 * sigma**2)))
#   print(f_val)


# fig, ax = plt.subplots()
# ax.imshow(gauss, interpolation="none")

# x = [(i + 1)*50 for i in x]
# y = [(i + 1)*50 for i in y]

# ax.scatter(x[0], y[0], c="r", marker="o")
# ax.text(x[0], y[0], "start", fontdict={"c":"red"})
# ax.scatter(x[-1], y[-1], c="r", marker="o")
# ax.text(x[-1], y[-1], "end", fontdict={"c":"red"})
# ax.scatter(x, y, marker="None", c="b")
# ax.plot(x, y, "black", alpha=0.4)

# ax.add_patch(plt.Circle((n/2, n/2), math.floor(scaled*n/2), color='r', fill=False, alpha=0.25))

# plt.title("Continuous Selective-Stopping (threshold=%1.2f)" %threshold)
# plt.figtext(0.5, 0.01, "Agent performs selective-stopping with random orientation and constant step-size; terminates at concentration ≥ %1.2f." %threshold, wrap=True, horizontalalignment="center", fontsize=10)
# plt.xticks([])
# plt.yticks([])
# plt.show()