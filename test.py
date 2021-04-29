import numpy as np
import math

kf = 0

E_a = -np.log(kf)

kb = math.exp(- (E_a + 1))

print(kb)