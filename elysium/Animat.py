import math, numpy as np, matplotlib.pyplot as plt
from enum import Enum
from globals import START_Y, CTRL1_X, CTRL1_Y, CTRL2_X, CTRL2_Y, END_Y, O, S, BAT
from utils import sigmoid
from Env import EnvObjectTypes, Env

np.set_printoptions(precision=5)

class Sides(Enum):
  """
  Sides of an animat

  ...

  Attributes
  ----------
  LEFT : int
    left side
  RIGHT : int
    right side
  """

  LEFT = 0
  RIGHT = 1
  
class Link:
  """
  A class representing sensorimotor links

  ...

  Attributes
  ----------
  N_GENES : int
    number of genes needed to encode a sensorimotor link
  N_LINKS_PER_TYPE : int
    number of links connected to a motor per type
  ctrl_x : list
    x-coordinates of control phenotypes
  ctrl_y : list
    y-coordinates of control phenotypes
  O : float
    offset phenotype
  S : float
    slope modulation phenotype
  bat_side : int
    battery phenotype (side)
  """

  N_GENES = 9
  N_LINKS_PER_TYPE = 3

  def __init__(self, genome):
    """
    Parameters
    ----------
    genome : list
      A list of genes as a float between 0 and 1
    """
    self.set_phenome(genome)

  def set_phenome(self, genome):
    """Sets the phenotype of the 
    """
    if genome[CTRL1_X] > genome[CTRL2_X]:
      # enforce control point 2 follows control point 1
      genome[CTRL1_X], genome[CTRL2_X] = genome[CTRL2_X], genome[CTRL1_X]
    self.ctrl_x = [0] + [genome[CTRL1_X], genome[CTRL2_X]] + [1] # (0,1)
    self.ctrl_y = np.array([genome[START_Y], genome[CTRL1_Y], genome[CTRL2_Y], genome[END_Y]]) * 2.0 - 1.0 # (-1,1)
    self.O = genome[O] * 2.0 - 1.0 # (-1,1)
    self.S = genome[S] # (0,1)
    self.bat_side = int(genome[BAT] < 0.5) # 0 or 1

  def get_output(self, input, batteries):
    out = np.interp(input, self.ctrl_x, self.ctrl_y)
    B = batteries[self.bat_side]
    out = out + B * self.O # offset (-1,1)
    out = out + out * (B * 2.0 - 1.0) * self.S # multiply (-1,1), i.e. double or cancel
    out = max(min(out, 1.0), -1.0)
    return out
  
  def print(self):
    print('ctrl: ({: 0.2f},{: 0.2f}) ({: 0.2f},{: 0.2f}) ({: 0.2f},{: 0.2f}) ({: 0.2f},{: 0.2f}),\tO: {: 0.2f},\tS: {: 0.2f},\tbat_s:'.format(self.ctrl_x[0], self.ctrl_y[0], self.ctrl_x[1], self.ctrl_y[1], self.ctrl_x[2], self.ctrl_y[2], self.ctrl_x[3], self.ctrl_y[3], self.O, self.S), self.bat_side)

  def plot(self, plot_immediately=True):
    plt.plot(self.ctrl_x, self.ctrl_y, '-')
    if plot_immediately:
      plt.show()

class Animat:
  """
  A class used to represent an Animat

  ...

  Attributes
  ----------
  N_LINKS : int
    number of sensorimotor links per side
  N_GENES : int
    total number of genes that make up an animat
  MAX_BATTERY : int
    maximum battery level
  MAX_LIFE : int
    maximum number of iterations an animat can live
  RADIUS : int
    size of animats
  SENSOR_ANGLES : list
    left and right sensor angles relative to the animat's orientation, respectively

  Methods
  -------
  set_motor_states(plot=False)
    #TODO
  update(env)
    #TODO
  """

  N_LINKS = len(EnvObjectTypes) * Link.N_LINKS_PER_TYPE
  MAX_BATTERY = 200
  MAX_LIFE = 800
  RADIUS = 5
  SENSOR_ANGLES = [math.pi/4, -math.pi/4]

  def __init__(self, genome=None, thresholds=None):
    if genome is None:
      self.genome = [np.random.rand(Link.N_GENES) for _ in range(Animat.N_LINKS)]
    else:
      self.genome = genome

    # if thresholds is None:
    #   self.thresholds = np.random.rand(2) * 6.0 - 3.0 # (-3,3) array of two
    # else:
    #   self.thresholds = thresholds

    self.links = [Link(self.genome[link]) for link in range(Animat.N_LINKS)]
    for link in self.links:
      link.plot(False)
    plt.show()
    # self.x = np.random.randint(Env.MAX_X+1) # (0,200)
    # self.y = np.random.randint(Env.MAX_Y+1)
    # self.theta = np.random.rand() * 2*math.pi
    # self.dx = 0
    # self.dy = 0
    # self.dtheta = 0
    # self.min_dist_sq = [math.inf] * len(EnvObjectTypes)
    # self.closest_objects = [None] * len(EnvObjectTypes)
    # self.batteries = [Animat.MAX_BATTERY, Animat.MAX_BATTERY]
    # self.motor_states = [0.0, 0.0]
    # self.status = 'alive'
    # self.fitness = 0

  def print(self, *args):
    if 'genes' in args:
      for link in self.genome:
        print(str(link).replace('\n', ''))
  
  def set_motor_states(self, plot=False):
    # larger falloff means farther sight
    falloff = 1
    for side in Sides:
      # all link outputs summed at one motor
      sum = 0

      sens_angle = self.theta + self.SENSOR_ANGLES[side.value]
      sens_x_pos = self.x + self.RADIUS * math.cos(sens_angle)
      sens_y_pos = self.y + self.RADIUS * math.sin(sens_angle)
      
      for type in EnvObjectTypes:
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
    self.dtheta = (self.motor_states[Sides.LEFT.value] + self.motor_states[Sides.RIGHT.value]) / (Animat.RADIUS*2)

    if plot:
      plt.plot(self.x, self.y, 'o', color='black')
      plt.arrow(self.x, self.y, 10*math.cos(self.theta + self.SENSOR_ANGLES[0]), 10*math.sin(self.theta + self.SENSOR_ANGLES[0]), head_width=1, head_length=1)
      plt.arrow(self.x, self.y, 10*math.cos(self.theta + self.SENSOR_ANGLES[1]), 10*math.sin(self.theta + self.SENSOR_ANGLES[1]), head_width=1, head_length=1)
      for obj in self.closest_objects:
        plt.plot(obj.x, obj.y, 'o', label=obj.type)
      plt.xlim(0, Env.MAX_X)
      plt.ylim(0, Env.MAX_Y)
      plt.legend()
      plt.show()
  
  def update(self, env):
    self.x += self.dx
    self.y += self.dy
    self.theta += self.dtheta

    for object in EnvObjectTypes:
      if math.sqrt(self.min_dist_sq[object.value]) <= Animat.RADIUS:
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

def test(fn):
  if fn == 'link':
    link = Link([1, 0.33, 0, 0.66, 1, 0, 0, 0, 0])
    link.plot()
    link = Link([1, 0.33, 0, 0.66, 0, 1, 0, 0, 0])
    link.plot()
    link = Link([0, 0.5, 0.5, 1, 1, 0, 0, 0, 0])
    link.plot()
  elif fn == 'animat printing':
    animat = Animat()
    animat.print('genes')


if __name__ == '__main__':
  test('link')