import random
from utils import rand_float

class Reaction:
  def __init__(self, lhs, rhs):
    self.lhs = lhs
    self.rhs = rhs
    self.frc = random.uniform(0, 0.1)
    self.system = []

  def __repr__(self):
    return '\n<Reaction\n' + '\n '.join(('{}: {}'.format(item, self.__dict__[item]) for item in self.__dict__)) + '>'
    
  def __str__(self):
    return  '<class Reaction>' + '\n'+ ', '.join(('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__))