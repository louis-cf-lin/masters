import numpy as np
import matplotlib.pyplot as plt

# x = [.35,.5,.6,.7,.7]
x = [.5,.5,.5,.5,.5,.5,.5,.5,.5,.5,.5,.5,.5,.5,.5,.5,.5,.5,.5,.5]

out = [1]

for val in x:
  out.append(out[-1] * (1 + val)) 

yr = [0,1,2,3,4,5]

plt.plot(range(len(x)), out)
plt.show()