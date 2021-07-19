import numpy as np

def sigmoid(x, thold):
  y = 1/(1 + np.exp(-x - thold))
  return y