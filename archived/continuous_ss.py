import numpy as np
import matplotlib.pyplot as plt
import random as random
import math as math

n = 100
threshold = 0.95

mesh_x, mesh_y = np.meshgrid(np.linspace(-1,1,n), np.linspace(-1,1,n)) 
dst = np.sqrt(mesh_x*mesh_x + mesh_y*mesh_y) 
sigma = 1
muu = 0.000
gauss = np.exp(-((dst-muu)**2 / (2.0 * sigma**2))) 
scaled = np.sqrt(np.log(threshold) * -(2 * sigma**2))

x = [random.uniform(-1,1)]
y = [random.uniform(-1,1)]

d_x = 0
# d_y = 0
d_theta = 0

f_val = np.exp(-((np.sqrt(x[-1]*x[-1] + y[-1]*y[-1]) - muu)**2 / (2.0 * sigma**2)))

while (f_val <= threshold):
  if (x[-1] < -1 or x[-1] > 1 or y[-1] < -1 or y[-1] > 1):
    x.pop()
    y.pop()
  d_theta = random.uniform(0, 360)
  d_x = 0.1
  x.append(d_x*math.cos(d_theta) + x[-1])
  y.append(d_x*math.sin(d_theta) + y[-1])
  f_val = np.exp(-((np.sqrt(x[-1]*x[-1] + y[-1]*y[-1]) - muu)**2 / (2.0 * sigma**2)))
  print(f_val)


fig, ax = plt.subplots()
ax.imshow(gauss, interpolation="none")

x = [(i + 1)*50 for i in x]
y = [(i + 1)*50 for i in y]

ax.scatter(x[0], y[0], c="r", marker="o")
ax.text(x[0], y[0], "start", fontdict={"c":"red"})
ax.scatter(x[-1], y[-1], c="r", marker="o")
ax.text(x[-1], y[-1], "end", fontdict={"c":"red"})
ax.scatter(x, y, marker="None", c="b")
ax.plot(x, y, "black", alpha=0.4)

ax.add_patch(plt.Circle((n/2, n/2), math.floor(scaled*n/2), color='r', fill=False, alpha=0.25))

plt.title("Continuous Selective-Stopping (threshold=%1.2f)" %threshold)
plt.figtext(0.5, 0.01, "Agent performs selective-stopping with random orientation and constant step-size; terminates at concentration ≥ %1.2f." %threshold, wrap=True, horizontalalignment="center", fontsize=10)
plt.xticks([])
plt.yticks([])
plt.show()