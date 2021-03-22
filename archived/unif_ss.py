import numpy as np
import matplotlib.pyplot as plt
import random as random
import math as math

n = 100
threshold = 0.95

x, y = np.meshgrid(np.linspace(-1,1,n), np.linspace(-1,1,n)) 
dst = np.sqrt(x*x + y*y) 

sigma = 1
muu = 0.000

gauss = np.exp(-((dst-muu)**2 / (2.0 * sigma**2))) 

scaled = np.sqrt(np.log(threshold) * -(2 * sigma**2))

walk_x = [random.randrange(n)]
walk_y = [random.randrange(n)]

while (gauss[walk_x[-1], walk_y[-1]] <= threshold):
  direc = random.randrange(8)
  if direc == 0:
    walk_x.append(walk_x[-1])
    walk_y.append(walk_y[-1] - 1)
  elif direc == 1:
    walk_x.append(walk_x[-1] + 1)
    walk_y.append(walk_y[-1] - 1)
  elif direc == 2:
    walk_x.append(walk_x[-1] + 1)
    walk_y.append(walk_y[-1])
  elif direc == 3:
    walk_x.append(walk_x[-1] + 1)
    walk_y.append(walk_y[-1] + 1)
  elif direc == 4:
    walk_x.append(walk_x[-1])
    walk_y.append(walk_y[-1] + 1)
  elif direc == 5:
    walk_x.append(walk_x[-1] - 1)
    walk_y.append(walk_y[-1] + 1)
  elif direc == 6:
    walk_x.append(walk_x[-1] - 1)
    walk_y.append(walk_y[-1])
  else:
    walk_x.append(walk_x[-1] - 1)
    walk_y.append(walk_y[-1] - 1)

  if walk_x[-1] >= n or walk_x[-1] < 0 or walk_y[-1] >= n or walk_y[-1] < 0:
    walk_x.pop()
    walk_y.pop()

  print(gauss[walk_x[-1], walk_y[-1]])

fig, ax = plt.subplots()
ax.imshow(gauss, interpolation="none")


ax.scatter(walk_x[0], walk_y[0], c="r", marker="o")
ax.text(walk_x[0], walk_y[0], "start", fontdict={"c":"red"})
ax.scatter(walk_x[-1], walk_y[-1], c="r", marker="o")
ax.text(walk_x[-1], walk_y[-1], "end", fontdict={"c":"red"})
ax.scatter(walk_x, walk_y, marker="None", c="b")
ax.plot(walk_x, walk_y, "black", alpha=0.4)

ax.add_patch(plt.Circle((n/2, n/2), math.floor(scaled*n/2), color='r', fill=False, alpha=0.25))

plt.title("Uniform Selective-Stopping (threshold=%1.2f)" %threshold)
plt.figtext(0.5, 0.01, "Agent performs selective-stopping with uniformly random probability in a Gaussian medium and terminates at concentration ≥ %1.2f." %threshold, wrap=True, horizontalalignment="center", fontsize=10)
plt.xticks([])
plt.yticks([])
plt.show()