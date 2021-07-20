import matplotlib.pyplot as plt, numpy as np

x, y = np.linspace(0,1,100)

for index, value in enumerate(x):
  y[index] = value

plt.plot()