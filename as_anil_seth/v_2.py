import math
import numpy as np
from enum import Enum
import matplotlib.pyplot as plt

START_Y = 0
CTRL1_X = 1
CTRL1_Y = 2
CTRL2_X = 3
CTRL2_Y = 4
END_Y = 5
O = 6
S = 7
BAT = 8

L_SGMD = 9
R_SGMD = 10

class Entity(Enum):
  FOOD = 0
  WATER = 1
  TRAP = 2

class Object:
  radius = 16
  def __init__(self, type):
    self.type = type
    self.x = np.random.randint(201) # (0,200)
    self.y = np.random.randint(201)

class Env:
  N_OBJECTS = [3,3,9]
  def __init__(self):
    self.objects = [[Object(str(type.name)) for _ in range(Env.N_OBJECTS[type.value])] for type in Entity]
    print(self.objects)

  def get_closest_objects(self, animat):

    for type_index, type_objects in enumerate(self.objects):
      min_dist = math.inf
      for object_index, object in enumerate(type_objects):
        dist = (animat.x - object.x)**2 + (animat.y - object.y)**2 # efficient euclidean distance
        if dist < min_dist:
          min_dist = dist
          animat.closest[type_index] = object_index

class Link:
  N_GENES = 9
  def __init__(self, genome):
    self.set_genome(genome)

  def set_genome(self, genome):
    if genome[CTRL1_X] > genome[CTRL2_X]:
      # enforce control point 2 follows control point 1
      genome[CTRL1_X], genome[CTRL2_X] = genome[CTRL2_X], genome[CTRL1_X]
    self.ctrl_x = [0] + [genome[CTRL1_X], genome[CTRL2_X]] + [1] # (0,1)
    self.ctrl_y = np.array([genome[START_Y], genome[CTRL1_Y], genome[CTRL2_Y], genome[END_Y]]) * 2.0 - 1.0 # (-1,1)
    self.O = genome[O] # (-1,1)
    self.S = genome[S] # (0,1)
    self.infl_bat = genome[BAT]

  def output(self, input, battery):
    out = np.interp(input, self.ctrl_x, self.ctrl_y)
    unscaled = out

    B = battery[self.infl_bat]
    out = out + B * self.O # offset (-1,1)
    out = out + out * (B * 2.0 - 1.0) * self.S # multiply (-1,1), i.e. double or cancel

    out = max(min(out, 1.0), -1.0)
    
    return out, unscaled

class Animat:
  N_LINKS_PER_SENSOR = 3
  N_SENSORS_PER_MOTOR = 3
  N_MOTORS_PER_SIDE = 1
  N_SIDES = 1 # symmetric
  N_LINKS = N_SIDES * N_MOTORS_PER_SIDE * N_SENSORS_PER_MOTOR * N_LINKS_PER_SENSOR
  N_GENES = N_LINKS * Link.N_GENES

  radius = 5

  def __init__(self, genome=None):
    if genome is None:
      self.genome = np.random.rand(Animat.N_GENES)
    else:
      self.genome = genome
      
    self.links = [Link(self.genome[link_index*Link.N_GENES:link_index*Link.N_GENES+Link.N_GENES]) for link_index in range(Animat.N_LINKS)]
    print(self.links)

    self.x = np.random.randint(201) # (0,200)
    self.y = np.random.randint(201)

env = Env()
dude = Animat()

env.get_closest_object(dude, 'food')

for link in dude.links:
  plt.plot(link.ctrl_x, link.ctrl_y)

print('stop right there')