import math
import numpy as np

class Animat:
  def __init__(self):
    self.genes = [np.random.randint(100, size=(9)) for _ in range(9)] # [0,99] inclusive
    self.set_second_threshold() 
    self.l_sigmoid = np.random.randint(100)
    self.r_sigmoid = np.random.randint(100)
    self.l_speed = None
    self.r_speed = None
    self.water = 200
    self.food = 200
  
  # enforce second threshold follows first
  def set_second_threshold(self):
    for link in self.genes:
      link[4] = np.random.randint(link[2], 100)

def scale(type, integer):
  if type == 'offset':
    return 200 * integer / 99 - 100
  elif type == 'threshold':
    return 200 * integer / 99 - 100
  elif type == 'gradient':
    return math.pi * integer / 99 - (math.pi / 2)
  elif type == 'offset_mod':
    return 2 * integer / 99 - 1
  elif type == 'slope_mod':
    return integer / 99
  elif type == 'sigmoid':
    return 6 * integer / 99 - 3
  elif type == 'speed':
    return 20 * integer / 99 - 10
  elif type == 'real_speed':
    return 5.6 * (integer + 10) / 20 - 2.8
  else:
    return

def calculate_gradient(angle):
  return 1/math.tan(angle)

def act_func(input, params, water, food):
  output = basic_shape(params, input)

  if params[8] % 2:
    battery = food
  else:
    battery = water
  output = offset_mod(params[7], output, battery)
  output = slope_mod(params[6], output, battery)

  return output

def basic_shape(params, input):
  if input <= params[2]:
    return params[0] + calculate_gradient(scale('gradient', params[1]))*input
  else:
    offset = params[0] + calculate_gradient(scale('gradient', params[1]))*params[2]
    if input <= params[4]:
      return offset + calculate_gradient(scale('gradient', params[3]))*(input - params[2])
    else:
      offset = offset + calculate_gradient(scale('gradient', params[3]))*(params[4] - params[2])
      return offset + calculate_gradient(scale('gradient', params[5]))*(input - params[4])

def offset_mod(O, input, battery):
  return input + (battery / 2 * scale('offset_mod', O))

def slope_mod(S, input, battery):
  return input + (input * (((battery - 100) / 100) * scale('slope_mod', S)))

def sigmoid(x, threshold):
  return 1/(1 + np.exp(-x - scale('sigmoid', threshold)))

def get_velocity(animat):
  l_v = 0
  r_v = 0
  dist = 50 # todo
  for i in range(9):
    l_v += act_func(dist, animat.genes[i], animat.water, animat.food)
    r_v += act_func(dist, animat.genes[i+9], animat.water, animat.food)
  animat.l_speed = scale('real_speed', scale('speed', sigmoid(l_v, animat.l_sigmoid)))
  animat.r_speed = scale('real_speed', scale('speed', sigmoid(r_v, animat.r_sigmoid)))


def trial():
  return

np.random.seed(814486224)
test = Animat()
print(test)

# params = [20, 74.25, 40, 24.75, 60, 74.25]

# def act_fun(input):
#   threshold = [40, 80]
  
#   if (input < threshold[0])