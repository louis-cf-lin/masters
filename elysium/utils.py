import numpy as np, math

def sigmoid(x, thold):
  y = 1/(1 + np.exp(-x - thold))
  return y
