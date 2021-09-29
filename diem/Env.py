import numpy as np, matplotlib.pyplot as plt, math
from enum import Enum

class EnvObjectTypes(Enum):
  FOOD = 0
  WATER = 1
  # TRAP = 2

class EnvObject:

  RADIUS = 0.05
  DECAY = 0.01

  def __init__(self, type, rstate = 2, loc = None):
    self.type = type
    self.rstate = np.random.default_rng(rstate)

    if loc is None:
      self.x = self.rstate.random() - 0.5
      self.y = self.rstate.random() - 0.5
    else:
      self.x = loc[0]
      self.y = loc[1]
  
  def __str__(self):
    return 'type: {}, x: {}, y: {}'.format(self.type, self.x, self.y)

  def __repr__(self):
    return 'type: {}, x: {}, y: {}'.format(self.type, self.x, self.y)
  
  def reset(self):
    self.x = self.rstate.random() - 0.5
    self.y = self.rstate.random() - 0.5

class Env:

  MAX_X = 0.5
  MAX_Y = 0.5
  MIN_X = -0.5
  MIN_Y = -0.5
  N_OBJECTS = [2, 2, 0]

  def __init__(self):
    self.objects = [[EnvObject(str(type.name), type.value * len(EnvObjectTypes) + i) for i in range(Env.N_OBJECTS[type.value])] for type in EnvObjectTypes]
    self.consumed = []
  
  def plot(self):
    colors = ['g', 'b', 'r']
    for type in EnvObjectTypes:
      for object in self.objects[type.value]:
        plt.gca().add_patch(plt.Circle((object.x, object.y), EnvObject.RADIUS, color=colors[type.value]))
    for object in self.consumed:
      plt.gca().add_patch(plt.Circle((object.x, object.y), EnvObject.RADIUS, color=colors[EnvObjectTypes[object.type].value], fill=False))
      

if __name__ == '__main__':
  env = Env()

