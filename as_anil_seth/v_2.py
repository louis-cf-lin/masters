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

def sigmoid(x, thold):
  y = 1/(1 + np.exp(-x - thold))
  return y

class Sides(Enum):
  LEFT = 0
  RIGHT = 1

class ObjectTypes(Enum):
  FOOD = 0
  WATER = 1
  TRAP = 2

class Object:
  radius = 16
  def __init__(self, type):
    self.type = type
    self.x = np.random.randint(201) # (0,200)
    self.y = np.random.randint(201)
    self.dist_from_animat = 0

class Env:
  N_OBJECTS = [1, 0, 0]
  def __init__(self):
    self.objects = [[Object(str(type.name)) for _ in range(Env.N_OBJECTS[type.value])] for type in ObjectTypes]
    print(self.objects)

  def get_min_dist(self, animat):
    for type_index, type_objects in enumerate(self.objects): # for each object type
      for object_index, object in enumerate(type_objects):
        object.dist_from_animat = (animat.x - object.x)**2 + (animat.y - object.y)**2 # efficient euclidean distance
        if object.dist_from_animat < animat.min_dist[type_index]:
          animat.min_dist[type_index] = object.dist_from_animat
          animat.closest_objects[type_index] = object
          # print(object_index)

    for type in ObjectTypes:
      animat.min_dist[type.value] = min(animat.min_dist[type.value], 200) # (0,200)
      animat.min_dist[type.value] = animat.min_dist[type.value] / 200 # (0,1)

    # print(animat.closest)
    # plt.plot(animat.x, animat.y, 'o', color='black')
    # colors = ['g', 'b', 'r']
    # for type in ObjectTypes:
    #   for obj in range(Env.N_OBJECTS[type.value]):
    #     plt.plot(self.objects[type.value][obj].x, self.objects[type.value][obj].y, 'o', c=colors[type.value])
    #     plt.annotate(obj, (self.objects[type.value][obj].x, self.objects[type.value][obj].y))
    
    # plt.xlim(0, 200)
    # plt.ylim(0, 200)
    # plt.show()

class Link:
  N_GENES = 9
  N_LINKS_PER_TYPE = 3
  def __init__(self, genome):
    self.set_genome(genome)

  def set_genome(self, genome):
    if genome[CTRL1_X] > genome[CTRL2_X]:
      # enforce control point 2 follows control point 1
      genome[CTRL1_X], genome[CTRL2_X] = genome[CTRL2_X], genome[CTRL1_X]
    self.ctrl_x = [0] + [genome[CTRL1_X], genome[CTRL2_X]] + [1] # (0,1)
    self.ctrl_y = np.array([genome[START_Y], genome[CTRL1_Y], genome[CTRL2_Y], genome[END_Y]]) * 2.0 - 1.0 # (-1,1)
    self.O = genome[O] * 2.0 - 1.0 # (-1,1)
    self.S = genome[S] # (0,1)
    self.infl_bat = int(genome[BAT] < 0.5) # 0 or 1

  def output(self, input, battery):
    out = np.interp(input, self.ctrl_x, self.ctrl_y)
    unscaled = out

    B = battery[self.infl_bat]
    out = out + B * self.O # offset (-1,1)
    out = out + out * (B * 2.0 - 1.0) * self.S # multiply (-1,1), i.e. double or cancel

    out = max(min(out, 1.0), -1.0)
        
    return out

class Animat:
  N_LINKS = len(ObjectTypes) * Link.N_LINKS_PER_TYPE
  N_GENES = N_LINKS * Link.N_GENES

  radius = 5

  def __init__(self, genome=None, tholds=None):
    if genome is None:
      self.genome = np.random.rand(Animat.N_GENES)
    else:
      self.genome = genome
      
    self.links = [Link(self.genome[link_index*Link.N_GENES:link_index*Link.N_GENES+Link.N_GENES]) for link_index in range(Animat.N_LINKS)]
    print(self.links)

    if tholds is None:
      self.tholds = np.random.rand(2) * 6.0 - 3.0
    else:
      self.tholds = tholds

    self.x = np.random.randint(201) # (0,200)
    self.y = np.random.randint(201)
    self.theta = np.random.rand() * 2*math.pi
    self.dx = 0
    self.dy = 0
    self.dtheta = 0
    self.min_dist = [math.inf] * len(ObjectTypes)
    self.closest_objects = [None] * len(ObjectTypes)
    self.battery = [1.0, 1.0]
    self.motor_states = [0.0, 0.0]
  
  def set_motor_states(self):
    link_index = 0
    l_out = 0
    r_out = 0
    for type in ObjectTypes: # 3


      for _ in range(Animat.N_LINKS_PER_SENSOR): # 3
        output_sum += self.links[link_index].output(self.min_dist[type.value], self.battery)
        link_index += 1
        
    self.motor_states[Sides.LEFT.value] = sigmoid(l_out, self.tholds[Sides.LEFT.value])
    self.motor_states[Sides.RIGHT.value] = sigmoid(r_out, self.tholds[Sides.RIGHT.value])
    


    magnitude = (self.motor_states[Sides.LEFT.value] + self.motor_states[Sides.RIGHT.value]) / 2
    self.dx = magnitude * math.cos(self.theta)
    self.dy = magnitude * math.sin(self.theta)
    self.dtheta = (self.motor_states[Sides.LEFT.value] + self.motor_states[Sides.RIGHT.value]) / (Animat.radius*2)

    print(self.motor_states)
  
  def update_position(self):
    self.x += self.dx
    self.y += self.dy
    self.theta += self.dtheta

def prepare_to_update(env, animat):
  env.get_min_dist(animat) # finds closest object of each type
  animat.set_motor_states()

def update(animat):
  animat.update_position()
  env.check_for


crib = Env()
dude = Animat()
prepare_to_update(crib, dude)
update(dude)


# for link in dude.links:
#   plt.plot(link.ctrl_x, link.ctrl_y)

print('stop right there')