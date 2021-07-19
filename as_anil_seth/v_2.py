import math, random
import numpy as np
from enum import Enum
import matplotlib.pyplot as plt

np.random.seed(100)

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

max_x = 200
max_y = 200

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
    self.x = np.random.randint(max_x+1) # (0,200)
    self.y = np.random.randint(max_y+1)
    self.dist_from_animat_sq = 0

class Env:
  N_OBJECTS = [1, 0, 0]
  def __init__(self):
    self.objects = [[Object(str(type.name)) for _ in range(Env.N_OBJECTS[type.value])] for type in ObjectTypes]

  def get_min_dist(self, animat):
    for type_index, type_objects in enumerate(self.objects): # for each object type
      for object in type_objects:
        object.dist_from_animat_sq = (animat.x - object.x)**2 + (animat.y - object.y)**2 # efficient euclidean distance
        if object.dist_from_animat_sq < animat.min_dist_sq[type_index]:
          animat.min_dist_sq[type_index] = object.dist_from_animat_sq
          animat.closest_objects[type_index] = object

    for type in ObjectTypes:
      animat.min_dist_sq[type.value] = min(animat.min_dist_sq[type.value], 200**2) # (0,40000)

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
  
  def set_new_object(self):
    for object_type in ObjectTypes: # for each object type
      for i, object in enumerate(self.objects[object_type.value]):
        if math.sqrt(object.dist_from_animat_sq) <= Animat.radius:
          self.objects[object_type.value][i] = Object(str(object_type.name))
          return

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

    # plt.plot(self.ctrl_x, self.ctrl_y)
    # plt.show()

  def get_output(self, input, batteries):
    out = np.interp(input, self.ctrl_x, self.ctrl_y)
    unscaled = out

    B = batteries[self.infl_bat]
    out = out + B * self.O # offset (-1,1)
    out = out + out * (B * 2.0 - 1.0) * self.S # multiply (-1,1), i.e. double or cancel

    out = max(min(out, 1.0), -1.0)
        
    return out

class Animat:
  N_LINKS = len(ObjectTypes) * Link.N_LINKS_PER_TYPE
  N_GENES = N_LINKS * Link.N_GENES

  MAX_BATTERY = 200.0
  MAX_LIFE = 800

  radius = 5
  sensor_angles = [math.pi/4, -math.pi/4]

  def __init__(self, genome=None, tholds=None):
    if genome is None:
      self.genome = np.random.rand(Animat.N_GENES)
    else:
      self.genome = genome
      
    self.links = [Link(self.genome[link_index*Link.N_GENES:link_index*Link.N_GENES+Link.N_GENES]) for link_index in range(Animat.N_LINKS)]

    if tholds is None:
      self.tholds = np.random.rand(2) * 6.0 - 3.0
    else:
      self.tholds = tholds

    self.x = np.random.randint(max_x+1) # (0,200)
    self.y = np.random.randint(max_y+1)
    self.theta = np.random.rand() * 2*math.pi
    self.dx = 0
    self.dy = 0
    self.dtheta = 0
    self.min_dist_sq = [math.inf] * len(ObjectTypes)
    self.closest_objects = [None] * len(ObjectTypes)
    self.batteries = [Animat.MAX_BATTERY, Animat.MAX_BATTERY]
    self.motor_states = [0.0, 0.0]
    self.status = 'alive'
    self.fitness = 0
  
  def set_motor_states(self):
    # larger falloff means farther sight
    falloff = 1
    for side in Sides:
      # all link outputs summed at one motor
      sum = 0

      sens_angle = self.theta + self.sensor_angles[side.value]
      sens_x_pos = self.x + self.radius * math.cos(sens_angle)
      sens_y_pos = self.y + self.radius * math.sin(sens_angle)
      
      for type in ObjectTypes:
        # print(side.name, type.name)
        obj_x_pos = self.closest_objects[type.value].x
        obj_y_pos = self.closest_objects[type.value].y

        d_sq = self.min_dist_sq[type.value] / 40000
        # print('distance squared:', d_sq)
        omni = falloff/(falloff+d_sq)

        # sensor to object vector
        s2o = [obj_x_pos - sens_x_pos, 
              obj_y_pos - sens_y_pos]

        s2o_mag = np.sqrt(s2o[0]**2 + s2o[1]**2)
        # normalise
        if s2o_mag > 0:
          s2o = [v / s2o_mag for v in s2o]
        
        # print('sensor to object vector:', s2o)

        # sensor direction unit vector
        sens_uv = [math.cos(sens_angle),
                    math.sin(sens_angle)]
        
        # print('sensor unit vector:', sens_uv)

        # positive component of sensor to object projection on sensor direction
        # print("projection:", s2o[0]*sens_uv[0] + s2o[1]*sens_uv[1])
        input = omni * max(0.0, s2o[0]*sens_uv[0] + s2o[1]*sens_uv[1])
        
        # map input to 
        for link in self.links[type.value*Link.N_LINKS_PER_TYPE:type.value*Link.N_LINKS_PER_TYPE+Link.N_LINKS_PER_TYPE]:

          sum += link.get_output(input, self.batteries)

      # print(sum)
      self.motor_states[side.value] = sigmoid(sum, self.tholds[side.value])

    magnitude = (self.motor_states[Sides.LEFT.value] + self.motor_states[Sides.RIGHT.value]) / 2
    self.dx = magnitude * math.cos(self.theta)
    self.dy = magnitude * math.sin(self.theta)
    self.dtheta = (self.motor_states[Sides.LEFT.value] + self.motor_states[Sides.RIGHT.value]) / (Animat.radius*2)


    plt.plot(self.x, self.y, 'o', color='black')
    plt.arrow(self.x, self.y, 10*math.cos(self.theta + self.sensor_angles[0]), 10*math.sin(self.theta + self.sensor_angles[0]), head_width=1, head_length=1)
    plt.arrow(self.x, self.y, 10*math.cos(self.theta + self.sensor_angles[1]), 10*math.sin(self.theta + self.sensor_angles[1]), head_width=1, head_length=1)
    for obj in self.closest_objects:
      plt.plot(obj.x, obj.y, 'o', label=obj.type)
    plt.xlim(0, max_x)
    plt.ylim(0, max_y)
    plt.legend()
    plt.show()
  
  def update(self, env):
    self.x += self.dx
    self.y += self.dy
    self.theta += self.dtheta

    for object in ObjectTypes:
      if math.sqrt(self.min_dist_sq[object.value]) <= Animat.radius:
        if object.name == 'TRAP':
          self.status = 'dead'
          return
        else:
          self.batteries[object.value] = Animat.MAX_BATTERY
          self.min_dist_sq[object.value] = math.inf
          env.set_new_object()
          return
    
    self.batteries = [battery - 1 for battery in self.batteries]
    if sum(self.batteries) <= 0:
      self.status = 'dead'


def prepare_to_update(env, animat):
  env.get_min_dist(animat) # finds closest object of each type
  animat.set_motor_states() # calculate outputs and set motors derivs

def update(env, animat):
  animat.update(env) # update x, y, theta

def trial(animat, env):
  x_traj = [None] * Animat.MAX_LIFE
  y_traj = [None] * Animat.MAX_LIFE
  fitness = 0

  for i in range(Animat.MAX_LIFE):
    x_traj[i] = animat.x
    y_traj[i] = animat.y
    prepare_to_update(env, animat)
    update(env, animat)
    fitness += sum(animat.batteries) / 400.0
    if animat.status == 'dead':
      break

  # for i in range(Animat.MAX_LIFE)[::2]:
  #   circle = plt.Circle((x_traj[i], y_traj[i]), Animat.radius, fill=False, alpha=0.25)
  #   plt.gca().add_patch(circle)

  # colors = ['g', 'b', 'r']
  # for i, obj in enumerate(animat.closest_objects):
  #   circle = plt.Circle((obj.x, obj.y), Object.radius, color=colors[i], label=obj.type, fill=False)
  #   plt.gca().add_patch(circle)
  # plt.legend()
  # plt.xlim(0, max_x)
  # plt.ylim(0, max_y)
  # plt.show()

  animat.fitness = fitness

class Population:
  SIZE = 100
  def __init__(self):
    self.animats = [Animat() for _ in range(Population.SIZE)]
  
  def evaluate(self, env):
    for animat in self.animats:
      trial(animat, env)

  def new_gen(self):
    new_animats = [None] * Population.SIZE
    max = np.max([animat.fitness for animat in self.animats])
    min = np.min([animat.fitness for animat in self.animats])
    i = 0
    while (None in new_animats):
      for animat in self.animats:
        p_selection = (animat.fitness - min) / (max - min + 1) # linear selection prob
        if np.random.rand() < p_selection:
          new_animats[i] = Animat(animat.genome)
          i += 1
          if i == Population.SIZE:
            self.animats = new_animats
            return

n_generations = 10

env = Env()
pop = Population()
min_fitness = [None] * n_generations
mean_fitness = [None] * n_generations
max_fitness = [None] * n_generations

for i in range(n_generations):
  pop.evaluate(env)
  min_fitness[i] = np.min([animat.fitness for animat in pop.animats])
  mean_fitness[i] = np.mean([animat.fitness for animat in pop.animats])
  max_fitness[i] = np.max([animat.fitness for animat in pop.animats])
  pop.new_gen()
  print(i, 'generation')

plt.plot(min_fitness)
plt.plot(mean_fitness)
plt.plot(max_fitness)
plt.show()

print('stop right there')