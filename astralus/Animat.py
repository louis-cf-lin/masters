import math, numpy as np, matplotlib.pyplot as plt
from enum import Enum
from globals import DT
from Network import Network
from Env import EnvObjectTypes, Env

class Sides(Enum):
  LEFT = 0
  RIGHT = 1
  
class Link:
  N_LINKS_PER_TYPE = 3

  def __init__(self):
    self.network = Network()

  def get_output(self, consumption):
    self.network.step()
    out = np.interp(consumption, self.ctrl_x, self.ctrl_y)
    out = max(min(out, 1.0), -1.0)
    return out

class Animat:
  N_LINKS = len(EnvObjectTypes) * Link.N_LINKS_PER_TYPE
  MAX_BATTERY = 1
  DRAIN_RATE = 0.08
  MAX_LIFE = 800
  RADIUS = 0.1

  def __init__(self):
    self.links = [[Link() for i in range(Link.N_LINKS_PER_TYPE)] for type in EnvObjectTypes]

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

    for side in Sides:
      # all link outputs summed at one motor
      sum = 0
      # sensor properties
      sens_orient = self.theta + self.SENSOR_ANGLES[side.value]
      sens_x = self.x + self.RADIUS * math.cos(sens_orient)
      sens_y = self.y + self.RADIUS * math.sin(sens_orient)
      # calculate reading for each sensor
      for type in EnvObjectTypes:
        consumption = 0

        for obj in env.objects[type.value]:
          consumption += np.exp(-((sens_x - obj.x)**2 + (sens_y - obj.y)**2) / 2000)

        plotting_values[side.value][type.value] = consumption
        for link in self.links[type.value]:
          sum += link.get_output(consumption)
      # set motor state
      self.motor_states[side.value] = min(1.0, sum / 3)

    # calculate derivs
    mag = (self.motor_states[Sides.LEFT.value] + self.motor_states[Sides.RIGHT.value]) / 2
    self.dx = mag * math.cos(self.theta)
    self.dy = mag * math.sin(self.theta)
    self.dtheta = (self.motor_states[Sides.RIGHT.value] - self.motor_states[Sides.LEFT.value]) / Animat.RADIUS

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

    self.x += self.dx * DT
    self.y += self.dy * DT
    self.theta += self.dtheta * DT
    self.batteries = [battery - Animat.DRAIN_RATE * DT for battery in self.batteries]
    
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

  def plot(self):
    plt.plot(self.x, self.y, 'ko', ms=1, alpha=0.5)
  
  def print(self, *args):
    if 'genes' in args:
      for link in self.genome:
        print(str(link).replace('\n', ''))


def map_env():
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

  test_animat_trial()

