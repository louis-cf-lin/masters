import math, numpy as np, matplotlib.pyplot as plt, copy, random
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
  return omni * max(0.0, s2o[0]*sens_uv[0] + s2o[1]*sens_uv[1])

class Animat:

  MAX_BATTERY = 1
  DRAIN_RATE = 0.01
  MAX_LIFE = 800
  RADIUS = 0.05
  SENSOR_ANGLES = [math.pi/4, -math.pi/4]

  def __init__(self, controller=None):
    if controller is None:
      self.controller = Network()
    else:
      self.controller = controller
    self.nearest = [None for _ in EnvObjectTypes]
    self.dsq = [None for _ in EnvObjectTypes]
    self.motor_hist = [[] for _ in Sides]
    self.sens_hist = [[[] for _ in EnvObjectTypes] for _ in Sides]
    self.dx = None
    self.dy = None
    self.dtheta = None

    # self.x = np.random.random()
    # self.y = np.random.random()
    # self.theta = np.random.random() * 2*math.pi
    self.x = 1
    self.x_hist = [self.x]
    self.y = -1
    self.y_hist = [self.y]
    self.theta = math.pi * 5 / 8

    self.battery = Animat.MAX_BATTERY
    self.battery_hist = [Animat.MAX_BATTERY]
    self.fitness = 0
    self.alive = True
  

  def __eq__(self, other) :
    return self.controller == other.controller and np.array_equal(self.nearest, other.nearest) and np.array_equal(self.dsq, other.dsq) and self.dx == other.dx and self.dy == other.dy and self.dtheta == other.dtheta
  

  def prepare(self, env):
    # store closest object of each type
    find_nearest(self, env)
    readings = np.zeros((len(Sides), len(EnvObjectTypes)))
    # sensor readings
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
        self.sens_hist[side.value][type.value].append(reading)
    # get chemical outputs
    left_out, right_out = self.controller.get_outputs(np.sum(readings[Sides.LEFT.value]), np.sum(readings[Sides.RIGHT.value]))
    
    # set motor state
    left_motor_state = min(1.0, left_out / len(EnvObjectTypes))
    right_motor_state = min(1.0, right_out / len(EnvObjectTypes))
    self.motor_hist[Sides.LEFT.value].append(left_motor_state)
    self.motor_hist[Sides.RIGHT.value].append(right_motor_state)
    # calculate derivs
    mag = (left_motor_state + right_motor_state) / 2
    self.dx = mag * math.cos(self.theta) * 0.05
    self.dy = mag * math.sin(self.theta) * 0.05
    self.dtheta = (right_motor_state - left_motor_state) / Animat.RADIUS * 0.05
  

  def update(self, env):
    # update position and orientation
    self.x += self.dx
    self.x_hist.append(self.x)
    self.y += self.dy
    self.y_hist.append(self.y)
    self.theta += self.dtheta
    # check if encountered any objects
    encountered = False
    for type in EnvObjectTypes:
      if self.dsq[type.value] <= Animat.RADIUS ** 2:
        encountered = copy.deepcopy(self.nearest[type.value])
        env.hist.append(encountered)
        self.nearest[type.value].reset()
        if encountered.type == 'FOOD' or encountered.type == 'WATER':
          self.battery += encountered.conc
        else:
          self.battery = 0
    if not encountered:
      self.battery -= Animat.DRAIN_RATE
    # update battery and env
    self.fitness += self.battery
    self.battery_hist.append(self.battery)
    if self.battery <= 0:
      self.alive = False
    env.update()


  def evaluate(self, env):
    for i in range(Animat.MAX_LIFE):
      self.prepare(env)
      self.update(env)
      if not self.alive:
        break
    if (i >= Animat.MAX_LIFE-1):
      print('died of old age')
  

  def plot(self):
    plt.plot(self.x_hist, self.y_hist, 'ko', ms=1, alpha=0.5)


def test_animat_trial(controller=None, plot=True):

  if controller is None:
    animat = Animat()
  else:
    animat = Animat(controller)
  
  env = Env()
  
  if plot:
    fig = plt.figure(constrained_layout=True, figsize=(16,8))
    plots = fig.subfigures(1, 2)
    ax = plots[0].subplots()
    ax.set_aspect('equal')
    # ax.set_xlim(Env.MIN_X, Env.MAX_X)
    # ax.set_ylim(Env.MIN_Y, Env.MAX_Y)
    ax.add_patch(plt.Circle((animat.x, animat.y), Animat.RADIUS, color='black', fill=False))

  animat.evaluate(env)

  if plot:
    animat.plot()
    ax.add_patch(plt.Circle((animat.x, animat.y), Animat.RADIUS, color='black'))
    env.plot()

    multiplots = plots[1].subfigures(2,2)

    ax0 = multiplots[0][0].subplots()
    ax0.set_title('Battery')
    ax0.plot(animat.battery_hist)

    ax1 = multiplots[0][1].subplots(2,1)
    ax1[0].set_title('Left sensors')
    ax1[0].plot(animat.sens_hist[Sides.LEFT.value][EnvObjectTypes.FOOD.value], color='r')
    ax1[1].set_title('Right sensors')
    ax1[1].plot(animat.sens_hist[Sides.RIGHT.value][EnvObjectTypes.FOOD.value], color='g')
    
    ax2 = multiplots[1][0].subplots(2,1)
    ax2[0].set_title('Left motor')
    ax2[0].plot(animat.motor_hist[Sides.LEFT.value], color='r')
    ax2[1].set_title('Right motor')
    ax2[1].plot(animat.motor_hist[Sides.RIGHT.value], color='g')
    
    ax3 = multiplots[1][1].subplots()
    ax3.set_title('Chemical concentrations')
    color = ['r','g','b','m']
    for (i, chemical) in enumerate(animat.controller.chemicals):
      if i < 4:
        ax3.plot(chemical.hist, label=chemical.formula, c=color[i], zorder=1)
      else:
        ax3.plot(chemical.hist, ':', label=chemical.formula, c='black', alpha=0.25, zorder=0)
    ax3.legend()

    plt.show()

  animat.controller.print_derivs()

  print(f'Score is {animat.fitness}')

  # for reaction in animat.controller.reactions:
  #   print(reaction)

if __name__ == '__main__':

  np.set_printoptions(precision=5)

  test_animat_trial()

