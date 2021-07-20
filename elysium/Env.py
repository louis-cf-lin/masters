import math, numpy as np, matplotlib.pyplot as plt
from enum import Enum
from globals import ANIMAT_RADIUS

class EnvObjectTypes(Enum):
  """
  Environment object types

  ...

  Attributes
  ----------
  FOOD : int
    food type
  WATER : int
    water type
  TRAP : int
    trap type
  """

  FOOD = 0
  WATER = 1
  TRAP = 2

class EnvObject:
  """
  Objects in environments

  ...

  Attributes
  ----------
  radius : int
    size of all environments objects
  type : str
    object type
  x : float
    x coordinate
  y : float
    y coordinate
  dist_from_animat_sq : float
    distance between object and animat squared
  
  Methods
  -------
  reset()
    moves the object to a random location in the environment
  
  print()
    Prints object attributes in human-readable format
  """

  radius = 16

  def __init__(self, type):
    """
    Parameters
    ----------
    type : str
      object type
    """
    self.type = type
    self.x = np.random.randint(Env.MAX_X+1) # (0,200)
    self.y = np.random.randint(Env.MAX_Y+1)
    self.dist_from_animat_sq = None
  
  def reset(self):
    """Moves the object to a random location in the environment
    """
    self.x = np.random.randint(Env.MAX_X+1)
    self.y = np.random.randint(Env.MAX_Y+1)
    self.dist_from_animat_sq = None
  
  def print(self):
    """Prints object attributes in human-readable format
    """
    print(self.type, '(', self.x, ',', self.y, ') dist from animat sq:', self.dist_from_animat_sq)

class Env:
  """
  A class used to represent an Environment
  
  Attributes
  ----------
  MAX_X : int
    maximum size of horizontal dimension
  MAX_Y : int
    maximum size of vertical dimension
  N_OBJECTS : list
    number of food, water, trap objects in an environment
  
  Methods
  -------
  get_min_dist(animat, plot=False)
    TODO
  """
  MAX_X = 200
  MAX_Y = 200
  N_OBJECTS = [3, 3, 9]
  def __init__(self):
    self.objects = [[EnvObject(str(type.name)) for _ in range(Env.N_OBJECTS[type.value])] for type in EnvObjectTypes]
  
  def plot(self, show_now = True):
    """Plots the environment

    Parameters
    ----------
    show_now : bool, optional
      Render the plot immediately
    """
    colors = ['g', 'b', 'r']
    markers = ['s', 'o', 'x']
    if show_now:
      plt.figure(figsize=(8,8))
      plt.xlim(0, Env.MAX_X)
      plt.ylim(0, Env.MAX_Y)
    for type in EnvObjectTypes:
      for object in self.objects[type.value]:
        plt.plot(object.x, object.y, color=colors[type.value], marker=markers[type.value])
    if show_now:
      plt.show()


def test(fn):
  env = Env()
  envObject = EnvObject('FOOD')
  if fn == 'reset':
    envObject.print()
    envObject.reset()
    envObject.print()

if __name__ == '__main__':
  test('reset')
