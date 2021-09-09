import math, numpy as np, matplotlib.pyplot as plt, copy
from enum import Enum
from Env import EnvObjectTypes, Env
from Network import Network

class Sides(Enum):

  LEFT = 0
  RIGHT = 1

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

  MAX_BATTERY = 1
  DRAIN_RATE = 0.004
  MAX_LIFE = 800
  RADIUS = 0.1
  SENSOR_ANGLES = [math.pi/4, -math.pi/4]

  def __init__(self, controller=None):
    if controller is None:
      self.controller = Network()
    else:
      self.controller = controller
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

    readings = np.zeros((len(Sides), len(EnvObjectTypes)))
    # store closest object of each type
    find_nearest(self, env)

    for side in Sides:
      # sensor properties
      sens_orient = self.theta + self.SENSOR_ANGLES[side.value]
      sens_x = self.x + self.RADIUS * math.cos(sens_orient)
      sens_y = self.y + self.RADIUS * math.sin(sens_orient)
      # calculate reading for each sensor
      for type in EnvObjectTypes:
        obj_x = self.nearest[type.value].x
        obj_y = self.nearest[type.value].y
        reading = get_sens_reading(obj_x, obj_y, sens_x, sens_y, sens_orient)
        readings[side.value][type.value] = reading

    left_out, right_out = self.controller.get_outputs(np.sum(readings[Sides.LEFT.value]), np.sum(readings[Sides.RIGHT.value]))
    
    # set motor state
    self.motor_states[Sides.LEFT.value] = min(1.0, left_out / len(EnvObjectTypes))
    self.motor_states[Sides.RIGHT.value] = min(1.0, right_out / len(EnvObjectTypes))

    # calculate derivs
    mag = (self.motor_states[Sides.LEFT.value] + self.motor_states[Sides.RIGHT.value]) / 2
    self.dx = mag * math.cos(self.theta) * 0.05
    self.dy = mag * math.sin(self.theta) * 0.05
    self.dtheta = (self.motor_states[Sides.RIGHT.value] - self.motor_states[Sides.LEFT.value]) / Animat.RADIUS * 0.05

    return readings[0][0], readings[1][0], self.motor_states[Sides.LEFT.value], self.motor_states[Sides.RIGHT.value]
  
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
    right_food = [None] * Animat.MAX_LIFE
    left_motor = [None] * Animat.MAX_LIFE
    right_motor = [None] * Animat.MAX_LIFE
    for i in range(Animat.MAX_LIFE):
      left_food[i], right_food[i], left_motor[i], right_motor[i] = self.prepare(env)
      encountered = self.update()
      if plot and encountered:
        colors = ['g', 'b', 'r']
        plt.gca().add_patch(plt.Circle((encountered['x'], encountered['y']), Animat.RADIUS, color=colors[encountered['type']], fill=False))
      if not self.alive:
        break
      if plot:
        self.plot()
    
    return left_food, right_food, left_motor, right_motor

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

  animat = Animat()
  
  plt.figure(figsize=(6,6))
  plt.xlim(Env.MIN_X, Env.MAX_X)
  plt.ylim(Env.MIN_Y, Env.MAX_Y)

  plt.gca().add_patch(plt.Circle((animat.x, animat.y), Animat.RADIUS, color='black', fill=False))
  
  animat.plot()

  left_food, right_food, left_motor, right_motor = animat.evaluate(env)

  plt.gca().add_patch(plt.Circle((animat.x, animat.y), Animat.RADIUS, color='black'))
  env.plot()

  fig, axs = plt.subplots(2)
  axs[0].set_title('Left sensors')
  axs[0].plot(left_food, color='g')
  axs[1].set_title('Right sensors')
  axs[1].plot(right_food, color='g')
  fig2, axs2 = plt.subplots(2)
  axs2[0].set_title('Left motor states')
  axs2[0].plot(left_motor, color='g')
  axs2[1].set_title('Right motor states')
  axs2[1].plot(right_motor, color='g')

  fig2, ax2 = plt.subplots()
  ax2.set_title('chemical concentrations')
  for chemical in animat.controller.chemicals:
    ax2.plot(chemical.hist, label=chemical.formula)
  ax2.legend()

  plt.show()

  animat.controller.print_derivs()

  for reaction in animat.controller.reactions:
    print(reaction)

if __name__ == '__main__':

  np.set_printoptions(precision=5)

  # test_dir_sensor()
  test_animat_trial()
