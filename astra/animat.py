import math, numpy as np
from enum import Enum
from Env import EnvObjectTypes

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
    """Sets the phenotype.

    Parameters
    ----------
    genome : list
      A list of genes represented by floats between 0 and 1
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
    """Maps an input signal to an output based on phenome transformation.

    Output signal is a float between 0 and 1.

    Parameters
    ----------
    input : float
      Input signal between 0 and 1
    batteries : list
      Left and right battery levels
    """
    out = np.interp(input, self.ctrl_x, self.ctrl_y)
    B = max(min(batteries[self.bat_side], 1.0), 0.0)
    out = out + B * self.O * 2.0
    out = out + out * (B * 2.0 - 1.0) * self.S # multiply (-1,1), i.e. double or cancel
    out = max(min(out, 1.0), -1.0)
    return out

def find_nearest(animat, env):
  for type in EnvObjectTypes:
    min_dsq = math.inf
    for object in env.objects[type.value]:
      dsq = (animat.x - object.x)**2 + (animat.y - object.y)**2
      if (dsq < min_dsq):
        min_dsq = dsq
        animat.dsq[type.value] = dsq
        animat.nearest[type.value] = object

def get_sens_reading(obj_x, obj_y, sens_x, sens_y, sens_orient):

  # larger falloff means farther sight
  falloff = 0.25

  d_sq = (sens_x - obj_x)**2 + (sens_y - obj_y)**2

  omni = falloff/(falloff + d_sq) # (0,1)
  
  # sensor to object vector
  s2o = [obj_x - sens_x, 
        obj_y - sens_y]
  s2o_mag = np.sqrt(d_sq)
  # normalise
  if s2o_mag > 0:
    s2o = [v / s2o_mag for v in s2o]
  # sensor direction unit vector
  sens_uv = [math.cos(sens_orient),
              math.sin(sens_orient)]

  # positive component of sensor to object projection on sensor direction
  return omni * max(0.0, s2o[0]*sens_uv[0] + s2o[1]*sens_uv[1]) # (0,1)

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
  prepare(env)
    #TODO
  update()
    #TODO
  plot(show_now=False)
    #TODO
  print(*args)
    #TODO
  """

  N_LINKS = len(EnvObjectTypes) * Link.N_LINKS_PER_TYPE
  MAX_BATTERY = 1
  DRAIN_RATE = 0.004
  MAX_LIFE = 800
  RADIUS = 0.1
  SENSOR_ANGLES = [math.pi/4, -math.pi/4]

  def __init__(self, genome=None):
    if genome is None:
      self.genome = [[np.random.rand(Link.N_GENES) for _ in range(Link.N_LINKS_PER_TYPE)] for _ in EnvObjectTypes]
    else:
      self.genome = genome
    
    self.fitness = 0
  
  def prepare(self, env):
    return
  
  def update(self):
    return

  def evaluate(self, env, plot=True):
    self.fitness = sum(sum(sum(genes) for genes in self.genome))
