import math, numpy as np, matplotlib.pyplot as plt, copy
from Sides import Sides
from Env import EnvObjectTypes, Env
from Network import Network
from graphviz import Digraph
from globals import DT


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
  falloff = 0.5

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

  FULL_BATTERY = 1
  DRAIN_RATE = 0.5
  MAX_LIFE = 16
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
    self.x = Env.MAX_X
    self.x_hist = [self.x]
    self.y = Env.MIN_Y
    self.y_hist = [self.y]
    self.theta = math.pi * 5 / 8

    self.battery = [Animat.FULL_BATTERY, Animat.FULL_BATTERY]
    self.battery_hist = [[self.battery[0]], [self.battery[1]]]
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
        readings[side.value][type.value] = reading * DT
        self.sens_hist[side.value][type.value].append(reading)
    # get chemical outputs
    left_out, right_out = self.controller.get_outputs(readings, self.battery)
    
    # set motor state
    left_motor_state = min(1.0, left_out)
    right_motor_state = min(1.0, right_out)
    self.motor_hist[Sides.LEFT.value].append(left_motor_state)
    self.motor_hist[Sides.RIGHT.value].append(right_motor_state)
    # calculate derivs
    mag = (left_motor_state + right_motor_state) / 2
    self.dx = mag * math.cos(self.theta) * DT
    self.dy = mag * math.sin(self.theta) * DT
    self.dtheta = (right_motor_state - left_motor_state) / Animat.RADIUS * DT


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
        env.consumed.append(encountered)
        self.nearest[type.value].reset()
        if encountered.type == 'FOOD' or encountered.type == 'WATER':
          self.battery[type.value] = Animat.FULL_BATTERY
        else:
          self.battery = [0, 0]
    if not encountered:
      self.battery = [max(0, bat - Animat.DRAIN_RATE*DT) for bat in self.battery]
    # update battery and env
    self.fitness += sum(self.battery)
    self.battery_hist[EnvObjectTypes.FOOD.value].append(self.battery[EnvObjectTypes.FOOD.value])
    self.battery_hist[EnvObjectTypes.WATER.value].append(self.battery[EnvObjectTypes.WATER.value])

    if any(b <= 0 for b in self.battery):
      self.alive = False


  def evaluate(self, env):
    for _ in range(math.floor(Animat.MAX_LIFE / DT)):
      self.prepare(env)
      self.update(env)
      if not self.alive:
        break

  def graph(self):
    dot = Digraph(comment='chem', engine='neato')

    label = ['OUT LEFT', 'OUT RIGHT', 'FOOD LEFT', 'FOOD RIGHT', 'WATER LEFT', 'WATER RIGHT']

    for i, chem in enumerate(self.controller.chemicals):
      atts = { 'fontsize': '10'}
      if i < len(label):
        dot.node(chem.formula, shape='rectangle', fillcolor='gold', style='filled', label=f'<<b>{label[i]}</b><br/>{chem.formula}>', **atts)
      else:
        dot.node(chem.formula, shape='rectangle', label=f'<{chem.formula}>', **atts)
    
    for rxn in self.controller.reactions:
      atts = {'fontsize' : '10'}
      dot.node(str(rxn), shape='plaintext', label=f'<<b>{str(rxn)}</b><br/>>', **atts)
      for lhs_chem in rxn.lhs:
        dot.edge(str(rxn), lhs_chem.formula)
      for rhs_chem in rxn.rhs:
        dot.edge(str(rxn), rhs_chem.formula)

    dot.format = 'png'
    dot.render('graph')


def test_animat_trial(env, controller=None, show=True, save=False, fname=''):

  if controller is None:
    animat = Animat()
  else:
    animat = Animat(controller)
    
  fig = plt.figure(constrained_layout=True, figsize=(16,8))
  plots = fig.subfigures(1, 2)
  ax = plots[0].subplots()
  ax.set_aspect('equal')
  # ax.set_xlim(Env.MIN_X, Env.MAX_X)
  # ax.set_ylim(Env.MIN_Y, Env.MAX_Y)
  ax.add_patch(plt.Circle((animat.x, animat.y), Animat.RADIUS, color='black', fill=False))

  animat.evaluate(env)

  
  ax.plot(animat.x_hist, animat.y_hist, 'ko', ms=1, alpha=0.5)
  ax.plot(animat.x_hist, animat.y_hist, ms=1, alpha=0.1)
  ax.add_patch(plt.Circle((animat.x, animat.y), Animat.RADIUS, color='black'))
  env.plot()

  multiplots = plots[1].subfigures(2,2)

  ax0 = multiplots[0][0].subplots()
  ax0.set_title('Battery')
  ax0.plot(animat.battery_hist[EnvObjectTypes.FOOD.value], color='g')
  ax0.plot(animat.battery_hist[EnvObjectTypes.WATER.value], color='b')

  ax1 = multiplots[0][1].subplots(2,1)
  ax1[0].set_title('Left sensors')
  ax1[0].plot(animat.sens_hist[Sides.LEFT.value][EnvObjectTypes.FOOD.value], color='g')
  ax1[0].plot(animat.sens_hist[Sides.LEFT.value][EnvObjectTypes.WATER.value], color='b')
  ax1[1].set_title('Right sensors')
  ax1[1].plot(animat.sens_hist[Sides.RIGHT.value][EnvObjectTypes.FOOD.value], color='g')
  ax1[1].plot(animat.sens_hist[Sides.RIGHT.value][EnvObjectTypes.WATER.value], color='b')
  
  ax2 = multiplots[1][0].subplots(2,1)
  ax2[0].set_title('Left motor')
  ax2[0].plot(animat.motor_hist[Sides.LEFT.value], color='r')
  ax2[1].set_title('Right motor')
  ax2[1].plot(animat.motor_hist[Sides.RIGHT.value], color='g')
  
  ax3 = multiplots[1][1].subplots()
  ax3.set_title('Chemical concentrations')
  color = ['r','g','b','c','m','y']
  labels = ['Out L','Out R','Food L','Food R','Water L','Water R']
  for (i, chemical) in enumerate(animat.controller.chemicals):
    if i < len(labels):
      ax3.plot(chemical.hist, label=f'{labels[i]} ({chemical.formula})', c=color[i], zorder=1)
    else:
      ax3.plot(chemical.hist, ':', label=chemical.formula, c='black', alpha=0.25, zorder=0)
  ax3.legend()

  if save:
    plt.savefig(f'best_animat{fname}')
  if show:
    plt.show()

  animat.controller.print_derivs()

  print(f'Score is {animat.fitness}')

  animat.graph()

  # for reaction in animat.controller.reactions:
  #   print(reaction)

if __name__ == '__main__':

  np.set_printoptions(precision=5)

  test_animat_trial(env=Env(0))
  test_animat_trial(env=Env(1))
  test_animat_trial(env=Env(2))


