import math, numpy as np, matplotlib.pyplot as plt
from enum import Enum
from globals import START_Y, CTRL1_X, CTRL1_Y, CTRL2_X, CTRL2_Y, END_Y, O, S, BAT
from utils import sigmoid
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
    B = batteries[self.bat_side] / Animat.MAX_BATTERY
    out = out + B * self.O # offset (-1,1)
    out = out + out * (B * 2.0 - 1.0) * self.S # multiply (-1,1), i.e. double or cancel
    out = max(min(out, 1.0), -1.0)
    return out
  
  def print(self):
    """Prints link attributes in human-readable format.
    """
    print('ctrl: ({: 0.2f},{: 0.2f}) ({: 0.2f},{: 0.2f}) ({: 0.2f},{: 0.2f}) ({: 0.2f},{: 0.2f}),\tO: {: 0.2f},\tS: {: 0.2f},\tbat_s:'.format(self.ctrl_x[0], self.ctrl_y[0], self.ctrl_x[1], self.ctrl_y[1], self.ctrl_x[2], self.ctrl_y[2], self.ctrl_x[3], self.ctrl_y[3], self.O, self.S), self.bat_side)

  def plot(self, plot_immediately=True):
    """Plots the unscaled phenome transformation mapping.

    Parameters
    ----------
    plot_immediately : bool
      If true, renders the plot immediately after plotting
    """
    plt.plot(self.ctrl_x, self.ctrl_y, '-')
    if plot_immediately:
      plt.show()

def find_nearest(animat, env):
  for type in EnvObjectTypes:
    min_dsq = math.inf
    for object in env.objects[type.value]:
      dsq = (animat.x - object.x)**2 + (animat.y - object.y)**2
      if (dsq < min_dsq):
        min_dsq = dsq
        animat.dsq[type.value] = dsq
        animat.nearest[type.value] = object

def get_input(obj_x, obj_y, sens_x, sens_y, sens_orient):

  # larger falloff means farther sight
  falloff = 0.25
  # sensor to object vector
  s2o = [obj_x - sens_x, 
        obj_y - sens_y]
  s2o_mag = np.sqrt(s2o[0]**2 + s2o[1]**2)
  # sensor to object distance
  scaled_d = min(s2o_mag, 200) / 200 # (0,1)
  omni = falloff/(falloff + scaled_d) # (0,1)
  # normalise
  if s2o_mag > 0:
    s2o = [v / s2o_mag for v in s2o]
  # sensor direction unit vector
  sens_uv = [math.cos(sens_orient),
              math.sin(sens_orient)]
  # positive component of sensor to object projection on sensor direction
  input = omni * max(0.0, s2o[0]*sens_uv[0] + s2o[1]*sens_uv[1]) # (0,1)

  return input

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
  MAX_BATTERY = 200
  MAX_LIFE = 800
  RADIUS = 0.025
  SENSOR_ANGLES = [math.pi/4, -math.pi/4]

  def __init__(self, genome=None, thresholds=None):
    if genome is None:
      self.genome = [[np.random.rand(Link.N_GENES) for _ in range(Link.N_LINKS_PER_TYPE)] for _ in EnvObjectTypes]
    else:
      self.genome = genome

    if thresholds is None:
      self.thresholds = np.random.rand(2) * 6.0 - 3.0 # (-3,3) array of two
    else:
      self.thresholds = thresholds

    self.links = [[Link(self.genome[type.value][i]) for i in range(Link.N_LINKS_PER_TYPE)] for type in EnvObjectTypes]

    self.nearest = [None for _ in EnvObjectTypes]
    self.dsq = [None for _ in EnvObjectTypes]
    self.motor_states = [None for _ in Sides]
    self.dx = None
    self.dy = None
    self.dtheta = None

    # self.x = np.random.randint(Env.MAX_X+1) # (0,200)
    # self.y = np.random.randint(Env.MAX_Y+1)
    # self.theta = np.random.rand() * 2*math.pi
    #  TODO set these back
    self.x = 0.5
    self.y = 0.5
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
      # calculate input for each type
      for type in EnvObjectTypes:
        obj_x = self.nearest[type.value].x
        obj_y = self.nearest[type.value].y
        input = get_input(obj_x, obj_y, sens_x, sens_y, sens_orient) # (0,1)
        plotting_values[side.value][type.value] = input
        for link in self.links[type.value]:
          sum += link.get_output(input, self.batteries)
      # set motor state
      self.motor_states[side.value] = (sum - 4.5) / 20 # negative motor states allow backwards travel

    # calculate derivs
    mag = (self.motor_states[Sides.LEFT.value] + self.motor_states[Sides.RIGHT.value]) / 2
    self.dx = mag * math.cos(self.theta)
    self.dy = mag * math.sin(self.theta)
    self.dtheta = (self.motor_states[Sides.LEFT.value] + self.motor_states[Sides.RIGHT.value]) / (Animat.RADIUS*2)

    return plotting_values[0][0], plotting_values[0][1], plotting_values[0][2], plotting_values[1][0], plotting_values[1][1], plotting_values[1][2] 
  
  def update(self):
    encountered = None
    for type in EnvObjectTypes:
      if math.sqrt(self.dsq[type.value]) <= Animat.RADIUS:
        if type.name == 'FOOD' or type.name == 'WATER':
          self.batteries[type.value] = Animat.MAX_BATTERY
          encountered = [self.nearest[type.value].x, self.nearest[type.value].y, type.value]
          # TODO set this back
          # self.nearest[type.value].reset()
          self.nearest[type.value].alternate([[0.25, 0.25], [0.75, 0.75]])
        else:
          self.alive = False
          return encountered

    if sum(self.batteries) <= 0:
      self.alive = False
      return encountered

    self.x += self.dx
    self.y += self.dy
    self.theta += self.dtheta
    self.batteries = [battery - 1 for battery in self.batteries]
    
    self.fitness += sum(self.batteries)
    
    return encountered

  def plot(self, show_now=True, color='black', alpha=0.1, arrows=False):
    plt.gca().add_patch(plt.Circle((self.x, self.y), self.RADIUS, color=color, fill=False, alpha=alpha))
    if arrows:
      plt.arrow(self.x, self.y, self.RADIUS*math.cos(self.theta+self.SENSOR_ANGLES[0]), self.RADIUS*math.sin(self.theta+self.SENSOR_ANGLES[0]), color='red', head_width=0.1, head_length=0.1)
      plt.arrow(self.x, self.y, self.RADIUS*math.cos(self.theta+self.SENSOR_ANGLES[1]), self.RADIUS*math.sin(self.theta+self.SENSOR_ANGLES[1]), color='red', head_width=0.1, head_length=0.1)
    if show_now:
      plt.show()
  
  def print(self, *args):
    if 'genes' in args:
      for link in self.genome:
        print(str(link).replace('\n', ''))


def test(protocol):
  if protocol == 'link':
    link = Link([1, 0.33, 0, 0.66, 1, 0, 0, 0, 0])
    link.plot()
    link = Link([1, 0.33, 0, 0.66, 0, 1, 0, 0, 0])
    link.plot()
    link = Link([0, 0.5, 0.5, 1, 1, 0, 0, 0, 0])
    link.plot()
  elif protocol == 'genes':
    animat = Animat()
    animat.print('genes')
    animat.plot()
  elif protocol == 'heatmap':
    fig, ax = plt.subplots()
    x = 0.25
    y = 0.25
    theta = math.pi/4
    values = np.zeros((200,200))
    for i in range(200):
      for j in range(200):
        values[i][j] = get_input(i, j, x, y, theta)
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
  # plt.xlim(0, Env.MAX_X)
  # plt.ylim(0, Env.MAX_Y)
  x = [None] * Animat.MAX_LIFE
  y = [None] * Animat.MAX_LIFE
  left_food = [None] * Animat.MAX_LIFE
  left_water = [None] * Animat.MAX_LIFE
  left_trap = [None] * Animat.MAX_LIFE
  right_food = [None] * Animat.MAX_LIFE
  right_water = [None] * Animat.MAX_LIFE
  right_trap = [None] * Animat.MAX_LIFE
  animat.plot(False, 'red', 1, True)
  for i in range(Animat.MAX_LIFE):
    left_food[i], left_water[i], left_trap[i], right_food[i], right_water[i], right_trap[i] = animat.prepare(env)
    encountered = animat.update()
    if not animat.alive:
      break
    if encountered:
      colors = ['g', 'b']
      markers = ['s', 'o']
      plt.plot(encountered[0], encountered[1], color=colors[encountered[2]], marker=markers[encountered[2]], alpha=0.25)
    x[i] = animat.x
    y[i] = animat.y
    animat.plot(False)
  plt.plot(x, y, color='black', alpha=0.25)
  animat.plot(False, 'green', 1, True)
  env.plot(False)

  fig, axs = plt.subplots(2)
  axs[0].set_title('Left')
  axs[0].plot(left_food, color='g')
  axs[0].plot(left_water, color='b')
  axs[0].plot(left_trap, color='r')
  axs[1].set_title('Right')
  axs[1].plot(right_food, color='g')
  axs[1].plot(right_water, color='b')
  axs[1].plot(right_trap, color='r')
  plt.show()

if __name__ == '__main__':

  np.set_printoptions(precision=5)
  np.random.seed(1)

  # test('heatmap')
  test_animat_trial()

