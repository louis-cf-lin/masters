import math
import numpy as np
import matplotlib.pyplot as plt
import copy
from collections import OrderedDict
from Sides import Sides
from Env import EnvObjectTypes, ConsumableTypes, Env
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
  falloff = 0.25

  d_sq = (sens_x - obj_x)**2 + (sens_y - obj_y)**2

  omni = falloff/(falloff + d_sq)  # (0,1)

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
    self.sens_hist = [[[] for _ in ConsumableTypes] for _ in Sides]
    self.encountered = []
    self.dx = None
    self.dy = None
    self.dtheta = None

    self.x = Env.MAX_X
    self.y = Env.MIN_Y
    self.theta = math.pi * 5 / 8
    self.x_hist = [self.x]
    self.y_hist = [self.y]

    self.battery = [Animat.FULL_BATTERY for _ in ConsumableTypes]
    self.battery_hist = [[battery] for battery in self.battery]
    self.fitness = 0
    self.alive = True

  def __eq__(self, other):
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
    left_out, right_out = self.controller.get_outputs(readings)

    # set motor state
    left_motor_state = left_out
    right_motor_state = right_out
    self.motor_hist[Sides.LEFT.value].append(left_motor_state)
    self.motor_hist[Sides.RIGHT.value].append(right_motor_state)
    # calculate derivs
    mag = (left_motor_state + right_motor_state) / 2
    self.dx = mag * math.cos(self.theta)
    self.dy = mag * math.sin(self.theta)
    self.dtheta = (right_motor_state - left_motor_state) / Animat.RADIUS

  def update(self, env, i):
    # update position and orientation
    self.x += self.dx * DT
    self.x_hist.append(self.x)
    self.y += self.dy * DT
    self.y_hist.append(self.y)
    self.theta += self.dtheta * DT
    # check if encountered any objects
    encountered = False
    for type in EnvObjectTypes:
      if self.dsq[type.value] <= Animat.RADIUS ** 2:
        encountered = copy.deepcopy(self.nearest[type.value])
        env.consumed.append(encountered)
        self.nearest[type.value].reset()
        if any(encountered.type == type.name for type in ConsumableTypes):
          self.battery[type.value] = Animat.FULL_BATTERY
          self.encountered.append({'time': i, 'type': type.value})
        else:
          self.battery = [0, 0]
      else:
        self.battery[type.value] = max(
            0.0, self.battery[type.value] - Animat.DRAIN_RATE*DT)
    # update battery and env
    self.fitness += sum(self.battery) * DT * 10
    for type in ConsumableTypes:
      self.battery_hist[type.value].append(self.battery[type.value])

    if sum(self.battery) <= 0:
      self.alive = False

  def evaluate(self, env):
    for i in range(math.floor(Animat.MAX_LIFE / DT)):
      self.prepare(env)
      self.update(env, i)
      if not self.alive:
        break


def test_animat_trial(env, controller=None, show=True, save=False, fname=''):

  if controller is None:
    animat = Animat()
  else:
    animat = Animat(controller)
  animat.evaluate(env)

  type_colors = ['g', 'b', 'r']
  sens_motor_subs = plt.figure(
      constrained_layout=True, figsize=(9, 6)).subplots(2, 1)
  sens_motor_subs[0].set_title('Left')
  sens_motor_subs[1].set_title('Right')
  for side in Sides:
    for type in EnvObjectTypes:
      sens_motor_subs[side.value].plot(animat.sens_hist[side.value][type.value],
                                       ':', label=f'{type.name} SENSOR', color=type_colors[type.value])
    sens_motor_subs[side.value].plot(
        animat.motor_hist[side.value], label=f'MOTOR', color='grey')

  if save:
    plt.savefig(f'plot-sensorimotors_{fname}')

  chem_colors = ['darkorange', 'navajowhite',
                 'darkgreen', 'limegreen', 'darkblue', 'blue']
  chem_labels = ['Out L', 'Out R', 'Food L', 'Food R', 'Water L', 'Water R']
  chem = plt.figure(constrained_layout=True, figsize=(12, 6)).subplots(2, 1)
  chem[0].set_title('Chemical concentrations')
  chem[1].set_title('Energy')
  total_chem = np.zeros(len(animat.controller.chemicals[0].hist))
  total_energy = np.zeros(len(animat.controller.chemicals[0].hist))
  for (i, chemical) in enumerate(animat.controller.chemicals):
    hist = chemical.hist
    energy = np.array(hist) * chemical.potential
    if i < len(chem_labels):
      kwargs = {'label': f'{chem_labels[i]} ({chemical.formula})',
                'c': chem_colors[i], 'alpha': 0.75, 'zorder': 1}
    else:
      kwargs = {'ls': ':', 'label': 'Other',
                'c': 'black', 'alpha': 0.2, 'zorder': 0}
    chem[0].plot(hist, **kwargs)
    chem[1].plot(energy, **kwargs)
    total_chem += hist
    total_energy += energy

  for type in EnvObjectTypes:
    for side in Sides:
      input_chem = animat.controller.chemicals[getattr(
          Network, f'{type.name}_{side.name}')]
      total_chem -= input_chem.hist
      total_energy -= np.array(input_chem.hist) * input_chem.potential

  chem[0].set_ylabel('Chemical concs')
  total_chem_plot = chem[0].twinx()
  total_chem_plot.plot(total_chem, c='darkviolet')
  total_chem_plot.set_ylabel('Total concs', color='darkviolet')

  chem[1].set_ylabel('Energy')
  total_energy_plot = chem[1].twinx()
  total_energy_plot.plot(total_energy, c='darkviolet')
  total_energy_plot.set_ylabel('Total energy', color='darkviolet')

  handles, labels = chem[0].get_legend_handles_labels()
  by_label = OrderedDict(zip(labels, handles))
  chem[0].legend(by_label.values(), by_label.keys())
  chem[1].legend(by_label.values(), by_label.keys())

  if save:
    plt.savefig(f'plot-chems_{fname}')

  lifetime = plt.figure(constrained_layout=True,
                        figsize=(10, 5)).subplots(1, 2)

  lifetime[0].set_title('Trajectory')
  lifetime[0].set_aspect('equal')
  lifetime[0].set_xlim(Env.MIN_X, Env.MAX_X)
  lifetime[0].set_ylim(Env.MIN_Y, Env.MAX_Y)
  lifetime[0].plot(animat.x_hist, animat.y_hist, 'ko', ms=1, alpha=0.5)
  lifetime[0].plot(animat.x_hist, animat.y_hist, ms=1, alpha=0.1)
  lifetime[0].add_patch(plt.Circle(
      (animat.x_hist[0], animat.y_hist[0]), Animat.RADIUS, color='black', fill=False))
  lifetime[0].add_patch(plt.Circle(
      (animat.x, animat.y), Animat.RADIUS, color='black'))
  env.plot(lifetime[0])

  lifetime[1].set_title('Battery')
  for type in ConsumableTypes:
    lifetime[1].plot(animat.battery_hist[type.value],
                     color=type_colors[type.value])

  if save:
    plt.savefig(f'plot-lifetime_{fname}')

  if show:
    plt.show()

  print(f'Score is {animat.fitness}')
