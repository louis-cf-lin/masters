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

class Env():
  def __init__(self):
    return