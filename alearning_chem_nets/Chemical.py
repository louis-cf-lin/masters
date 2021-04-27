from utils import rand_float

class Chemical:
  def __init__(self, formula):
    self.formula = formula
    self.potential = rand_float(0, 7.5)
    self.conc = rand_float(0, 2)
    self.inflow = rand_float(0, 1)
    self.decay = rand_float(0, 1)
    self.is_stimulus = False
    self.is_control = False
    self.is_output = False
    self.is_food = False
    self.delta = 0
  
  def __repr__(self):
    return '\n<Chemical ' + ', '.join(('{}: {}'.format(item, self.__dict__[item]) for item in self.__dict__)) + '>'
    
  def __str__(self):
    return  '<class Chemical>' + '\n'+ ', '.join(('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__))