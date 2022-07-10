import math, numpy as np, matplotlib.pyplot as plt, copy
from enum import Enum
from globals import START_Y, CTRL1_X, CTRL1_Y, CTRL2_X, CTRL2_Y, END_Y, O, S, BAT
from Env import EnvObjectTypes, Env

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

    self.links = [[Link(self.genome[type.value][i]) for i in range(Link.N_LINKS_PER_TYPE)] for type in EnvObjectTypes]

    self.nearest = [None for _ in EnvObjectTypes]
    self.dsq = [None for _ in EnvObjectTypes]
    self.motor_states = [None for _ in Sides]
    self.dx = None
    self.dy = None
    self.dtheta = None

    # self.x = np.random.random()
    # self.y = np.random.random()
    # self.theta = np.random.random() * 2*math.pi
    self.x = 0
    self.y = 0
    self.theta = 0

    self.batteries = [Animat.MAX_BATTERY for _ in Sides]
    self.fitness = 0
    self.alive = True
  
  def prepare(self, env):
    plotting_values = np.zeros((2, 3))

    # store closest object of each type
    find_nearest(self, env)

    for side in Sides:
      # all link outputs summed at one motor
      sum = 0
      # sensor properties
      sens_orient = self.theta + self.SENSOR_ANGLES[side.value]
      sens_x = self.x + self.RADIUS * math.cos(sens_orient)
      sens_y = self.y + self.RADIUS * math.sin(sens_orient)
      # calculate reading for each sensor
      for type in EnvObjectTypes:
        obj_x = self.nearest[type.value].x
        obj_y = self.nearest[type.value].y
        reading = get_sens_reading(obj_x, obj_y, sens_x, sens_y, sens_orient)
        plotting_values[side.value][type.value] = reading
        for link in self.links[type.value]:
          sum += link.get_output(reading, self.batteries)
      # set motor state
      self.motor_states[side.value] = min(1.0, sum / 3)
      print(self.motor_states[side.value])

    # calculate derivs
    mag = (self.motor_states[Sides.LEFT.value] + self.motor_states[Sides.RIGHT.value]) / 2
    self.dx = mag * math.cos(self.theta) * 0.05
    self.dy = mag * math.sin(self.theta) * 0.05
    self.dtheta = (self.motor_states[Sides.RIGHT.value] - self.motor_states[Sides.LEFT.value]) / Animat.RADIUS * 0.05

    return plotting_values[0][0], plotting_values[0][1], plotting_values[0][2], plotting_values[1][0], plotting_values[1][1], plotting_values[1][2]
  
  def update(self):
    encountered = None
    for type in EnvObjectTypes:
      if self.dsq[type.value] <= Animat.RADIUS ** 2:
        encountered = {
                      'x': self.nearest[type.value].x,
                      'y': self.nearest[type.value].y,
                      'type': type.value
                      }
        if type.name == 'FOOD' or type.name == 'WATER':
          self.batteries[type.value] = Animat.MAX_BATTERY
          self.nearest[type.value].reset()
        else:
          self.alive = False
          self.nearest[type.value].x = None
          self.nearest[type.value].y = None
          return encountered

    if sum(self.batteries) <= 0:
      self.alive = False
      return encountered

    self.x += self.dx
    self.y += self.dy
    self.theta += self.dtheta
    self.batteries = [battery - Animat.DRAIN_RATE for battery in self.batteries]
    
    self.fitness += sum(self.batteries) / Animat.MAX_LIFE
    
    return encountered

  def evaluate(self, env, plot=True):
    left_food = [None] * Animat.MAX_LIFE
    left_water = [None] * Animat.MAX_LIFE
    left_trap = [None] * Animat.MAX_LIFE
    right_food = [None] * Animat.MAX_LIFE
    right_water = [None] * Animat.MAX_LIFE
    right_trap = [None] * Animat.MAX_LIFE
    for i in range(Animat.MAX_LIFE):
      left_food[i], left_water[i], left_trap[i], right_food[i], right_water[i], right_trap[i] = self.prepare(env)
      encountered = self.update()
      if plot and encountered:
        colors = ['g', 'b', 'r']
        plt.gca().add_patch(plt.Circle((encountered['x'], encountered['y']), Animat.RADIUS, color=colors[encountered['type']], fill=False))
      if not self.alive:
        break
      if plot:
        self.plot()
    
    return left_food, left_water, left_trap, right_food, right_water, right_trap

  def plot_links(self):
    fig, axs = plt.subplots(len(EnvObjectTypes), Link.N_LINKS_PER_TYPE)
    for i, link_type in enumerate(self.links):
      for j, link in enumerate(link_type):
        axs[i, j].plot(link.ctrl_x, link.ctrl_y)
        axs[i, j].set_xlim(0, 1)
        axs[i, j].set_ylim(-1, 1)
    
    for ax, col in zip(axs[0], ['Link {}'.format(ind+1) for ind in range(Link.N_LINKS_PER_TYPE)]):
      ax.set_title(col)

    for ax, row in zip(axs[:,0], [obj.name for obj in EnvObjectTypes]):
      ax.set_ylabel(row)

    fig.tight_layout()
    plt.show()

  def plot(self):
    plt.plot(self.x, self.y, 'ko', ms=1, alpha=0.5)
  
  def print(self, *args):
    if 'genes' in args:
      for link in self.genome:
        print(str(link).replace('\n', ''))


def test_dir_sensor():
  fig, ax = plt.subplots()
  x = 0.25
  y = 0.25
  theta = math.pi/4
  values = np.zeros((200,200))
  for i in range(200):
    for j in range(200):
      values[i][j] = get_sens_reading(i, j, x, y, theta)
  ax.arrow(x, y, 5*math.cos(theta), 5*math.sin(theta), color='red', head_width=1, head_length=1)
  im = ax.imshow(values)
  ax.invert_yaxis()
  fig.colorbar(im)
  plt.show()


def test_animat_trial(genome=None, env=None):

  if genome is None:
    animat = Animat()
  else:
    animat = Animat(genome)

  if env is None:
    env = Env()
  
  plt.figure(figsize=(6,6))
  plt.xlim(Env.MIN_X, Env.MAX_X)
  plt.ylim(Env.MIN_Y, Env.MAX_Y)

  plt.gca().add_patch(plt.Circle((animat.x, animat.y), Animat.RADIUS, color='black', fill=False))
  
  animat.plot()

  left_food, left_water, left_trap, right_food, right_water, right_trap = animat.evaluate(env)

  plt.gca().add_patch(plt.Circle((animat.x, animat.y), Animat.RADIUS, color='black'))
  env.plot()

  fig, axs = plt.subplots(2)
  axs[0].set_title('Left sensors')
  axs[0].plot(left_food, color='g')
  axs[0].plot(left_water, color='b')
  axs[0].plot(left_trap, color='r')
  axs[1].set_title('Right sensors')
  axs[1].plot(right_food, color='g')
  axs[1].plot(right_water, color='b')
  axs[1].plot(right_trap, color='r')
  fig2, axs2 = plt.subplots(2)
  axs2[0].set_title('Left motor states')
  axs2[0].plot(left_food, color='g')
  axs2[1].set_title('Right motor states')
  axs2[1].plot(right_food, color='g')
  
  plt.show()

if __name__ == '__main__':

  np.set_printoptions(precision=5)

  # test_dir_sensor()
  test_animat_trial()

  # animat = Animat()
  # animat.plot_links()

