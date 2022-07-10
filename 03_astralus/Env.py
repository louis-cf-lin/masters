import numpy as np, matplotlib.pyplot as plt
from enum import Enum

class EnvObjectTypes(Enum):
  FOOD = 0
  WATER = 1
  TRAP = 2

class EnvObject:

  RADIUS = 0.1

  def __init__(self, type, rstate = 0, loc = None):
    self.type = type
    self.rstate = np.random.default_rng(rstate)

    if loc is None:
      self.x = self.rstate.random() * 2.0 - 1.0
      self.y = self.rstate.random() * 2.0 - 1.0
    else:
      self.x = loc[0]
      self.y = loc[1]
  
  def __str__(self):
    return 'type: {}, x: {}, y: {}'.format(self.type, self.x, self.y)

  def __repr__(self):
    return 'type: {}, x: {}, y: {}'.format(self.type, self.x, self.y)
  
  def reset(self):
    self.x = self.rstate.random() * 2.0 - 1.0
    self.y = self.rstate.random() * 2.0 - 1.0

class Env:

  MAX_X = 1
  MAX_Y = 1
  MIN_X = -1
  MIN_Y = -1
  N_OBJECTS = [1, 1, 3]

  def __init__(self):
    self.objects = [[EnvObject(str(type.name), type.value * len(EnvObjectTypes) + i) for i in range(Env.N_OBJECTS[type.value])] for type in EnvObjectTypes]

  def plot(self):
    colors = ['g', 'b', 'r']
    for type in EnvObjectTypes:
      for object in self.objects[type.value]:
        plt.gca().add_patch(plt.Circle((object.x, object.y), EnvObject.RADIUS, color=colors[type.value]))


if __name__ == '__main__':
  env = Env()

