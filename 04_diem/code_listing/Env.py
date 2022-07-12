import copy
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum
from globals import DT


class EnvObjectTypes(Enum):
  FOOD = 0
  WATER = 1


class ConsumableTypes(Enum):
  FOOD = 0
  WATER = 1


class EnvObject:

  RADIUS = 0.05
  DECAY = 0.25
  CONC_MAX = 1

  def __init__(self, type, rstate, loc=None):
    self.type = type
    self.conc = EnvObject.CONC_MAX
    self.rstate = np.random.default_rng(rstate)
    self.consume_time = None

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
    self.conc = EnvObject.CONC_MAX
    self.x = self.rstate.random() - 0.5
    self.y = self.rstate.random() - 0.5


class Env:

  MAX_X = 0.5
  MAX_Y = 0.5
  MIN_X = -0.5
  MIN_Y = -0.5
  N_OBJECTS = [2, 2, 0]

  def __init__(self, rstate):
    self.rstate = np.random.default_rng(rstate)
    self.objects = [[EnvObject(type=str(type.name), rstate=self.rstate) for i in range(
        Env.N_OBJECTS[type.value])] for type in EnvObjectTypes]
    self.consumed = []

  def update(self, i):
    for type in self.objects:
      for obj in type:
        if obj.conc <= 0:
          obj_copy = copy.deepcopy(obj)
          obj_copy.consume_time = i
          self.consumed.append(obj_copy)
          obj.reset()
        else:
          obj.conc -= EnvObject.DECAY * DT

  def plot(self, axis):
    colors = ['g', 'b', 'r']
    for type in EnvObjectTypes:
      for object in self.objects[type.value]:
        axis.add_patch(plt.Circle((object.x, object.y),
                       EnvObject.RADIUS, color=colors[type.value]))
    for object in self.consumed:
      axis.add_patch(plt.Circle((object.x, object.y), EnvObject.RADIUS,
                     color=colors[EnvObjectTypes[object.type].value], fill=False))
