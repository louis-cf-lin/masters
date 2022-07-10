import numpy as np, matplotlib.pyplot as plt
from enum import Enum

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
  RADIUS : int
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

  RADIUS = 0.1

  def __init__(self, type, rstate = 0, loc = None):
    """
    Parameters
    ----------
    type : str
      object type
    """
    self.type = type
    self.rstate = np.random.RandomState(rstate)

    if loc is None:
      self.x = self.rstate.random() * 2.0 - 1.0
      self.y = self.rstate.random() * 2.0 - 1.0
    else:
      self.x = loc[0]
      self.y = loc[1]
    self.dist_from_animat_sq = None
  
  def reset(self):
    """Moves the object to a random location in the environment
    """
    self.x = self.rstate.random() * 2.0 - 1.0
    self.y = self.rstate.random() * 2.0 - 1.0
    self.dist_from_animat_sq = None
  

  def alternate(self, locs):
    """Toggles the object between two locations
    """
    if self.x == locs[0][0]:
      self.x = locs[1][0]
      self.y = locs[1][1]
    else:
      self.x = locs[0][0]
      self.y = locs[0][1]
  
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
  MAX_X = 1
  MAX_Y = 1
  MIN_X = -1
  MIN_Y = -1
  N_OBJECTS = [1, 1, 3]
  def __init__(self):
    self.objects = [[EnvObject(str(type.name), type.value * len(EnvObjectTypes) + i) for i in range(Env.N_OBJECTS[type.value])] for type in EnvObjectTypes]

  
  def plot(self):
    """Plots the environment

    Parameters
    ----------
    show_now : bool, optional
      Render the plot immediately
    """
    colors = ['g', 'b', 'r']
    for type in EnvObjectTypes:
      for object in self.objects[type.value]:
        plt.gca().add_patch(plt.Circle((object.x, object.y), EnvObject.RADIUS, color=colors[type.value]))



def test(fn):
  env = Env()
  envObject = EnvObject('FOOD')
  if fn == 'reset':
    envObject.print()
    envObject.reset()
    envObject.print()

if __name__ == '__main__':
  test('reset')
