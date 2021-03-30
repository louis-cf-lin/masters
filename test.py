import numpy as np
import matplotlib.pyplot as plt

def k_d(pos, element):
  kd = 1
  if element == 'M' or element == 'E':
    left = kd * np.exp(-((pos[0]-75)**2 + pos[1]**2) / 2000)
    right = kd * np.exp(-((pos[0]+75)**2 + pos[1]**2) / 2000)
    return left + right
  elif (element == 'S'):
    if np.sqrt((pos[0] + 75)**2 + (pos[1])**2) < 0.5:
      return 1
    else:
      return 0
  elif (element == 'F' or element == 'N'):
    return kd * np.exp(-(pos[0]**2 + pos[1]**2) / 2000)

sigma_x = 1.
sigma_y = 1.

x = 55
y = 0

print(k_d([45,0], 'M'))

# pos = [-75,0]

# print(np.sqrt((pos[0] + 75)**2 + (pos[1])**2))