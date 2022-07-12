import math
import numpy as np
import copy
from sides import Sides
from env import EnvObjectTypes, ConsumableTypes, Env
from network import Network
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

  # positive component of sensor to object projection on direction
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
    return self.controller == other.controller and \
        np.array_equal(self.nearest, other.nearest) and \
        np.array_equal(self.dsq, other.dsq) and \
        self.dx == other.dx and \
        self.dy == other.dy and \
        self.dtheta == other.dtheta

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
        reading = get_sens_reading(obj_x, obj_y, sens_x,
                                   sens_y, sens_orient)
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
        if any(encountered.type == type.name
               for type in ConsumableTypes):
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
