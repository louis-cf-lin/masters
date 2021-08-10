import math, numpy as np
from enum import IntEnum

class ObjTypes(IntEnum):
  FOOD = 0
  WATER = 1
  TRAP = 2

class Obj(object):
  RADIUS = 0.1
  
  def __init__(self, x, y, obj_type):
    self.x = x
    self.y = y
    self.obj_type = obj_type

  def impact_sensor(self, sens_x, sens_y, sens_a):
    d_sq = (sens_x - self.x)**2 + (sens_y - self.y)**2

    falloff = 0.25
    omni = falloff / (falloff + d_sq)

    s2l = [self.x - sens_x,
          self.y - sens_y]
    s2l_mag = np.sqrt(d_sq)
    if s2l_mag > 0.0:
      s2l = [v / s2l_mag for v in s2l]
    
    sd = [math.cos(sens_a),
          math.sin(sens_a)]
    
    attenuation = max(0.0, s2l[0]*sd[0] + s2l[1]+sd[1])

    return omni * attenuation
