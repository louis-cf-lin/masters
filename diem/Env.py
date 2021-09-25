import numpy as np, matplotlib.pyplot as plt, math
from enum import Enum

class EnvObjectTypes(Enum):
  FOOD = 0
  WATER = 1
  # TRAP = 2

class EnvObject:

  RADIUS = 0.1
  DECAY = 0.01
  MAX_CONC = 1

  def __init__(self, type, rstate = 2, loc = None):
    self.type = type
    self.rstate = np.random.default_rng(rstate)
    self.conc = EnvObject.MAX_CONC

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
  
  def update(self):
    # if not self.type == 'TRAP':
    #   self.conc = max(self.conc - EnvObject.DECAY, 0.1)
    return
  
  def reset(self):
    self.x = self.rstate.random() * 2.0 - 1.0
    self.y = self.rstate.random() * 2.0 - 1.0
    self.conc = EnvObject.MAX_CONC

class Env:

  MAX_X = 1
  MAX_Y = 1
  MIN_X = -1
  MIN_Y = -1
  N_OBJECTS = [2, 2, 0]

  def __init__(self):
    self.objects = [[EnvObject(str(type.name), type.value * len(EnvObjectTypes) + i) for i in range(Env.N_OBJECTS[type.value])] for type in EnvObjectTypes]
    self.hist = []

  def update(self):
    for type in self.objects:
      for obj in type:
        obj.update()
  
  def plot(self):
    colors = ['g', 'b', 'r']
    for type in EnvObjectTypes:
      for object in self.objects[type.value]:
        plt.gca().add_patch(plt.Circle((object.x, object.y), EnvObject.RADIUS, color=colors[type.value]))
        plt.text(object.x, object.y, round(object.conc, 3))
    for object in self.hist:
      plt.gca().add_patch(plt.Circle((object.x, object.y), EnvObject.RADIUS, color=colors[EnvObjectTypes[object.type].value], fill=False))
      plt.text(object.x, object.y, round(object.conc, 3))
      

if __name__ == '__main__':
  env = Env()

