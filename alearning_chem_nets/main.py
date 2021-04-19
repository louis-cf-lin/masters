import random, decimal

def concatenate(*args):
  return ''.join(*args)

def shuffle(chemical):
  return concatenate(random.sample(chemical, len(chemical)))

def order(chemical):
  return concatenate(sorted(chemical))

def rand_split(chemical):
  rand_pos = random.randrange(1, len(chemical)-1)
  return chemical[:rand_pos], chemical[rand_pos:]


def rand_float(lower, upper, digits=6):
  f = 10**digits
  return random.randint(lower*f, upper*f)/f

class Chemical:
  def __init__(self, formula, isFood):
    self.formula = formula
    self.potential = rand_float(0, 7.5)
    self.ic = rand_float(0, 2)
    if isFood:
      self.inflow = rand_float(0, 1)
    else:
      self.inflow = None
    self.decay = rand_float(0, 1)
  
  def __repr__(self):
    return '<Chemical ' + ' '.join(('{}: {}'.format(item, self.__dict__[item]) for item in self.__dict__)) + '>'
    
  def __str__(self):
    return  '<class Chemical>' + '\n'+ ', '.join(('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__))

class Reaction:
  def __init__(self, lhs, rhs):
    self.lhs = lhs
    self.rhs = rhs
    self.frc = rand_float(0, 0.1)

  def __repr__(self):
    return '<Reaction ' + ' '.join(('{}: {}'.format(item, self.__dict__[item]) for item in self.__dict__)) + '>'
    
  def __str__(self):
    return  '<class Reaction>' + '\n'+ ', '.join(('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__))

class Network:

  def __init__(self):
    self.chemical = []
    self.reactions = []

  def __repr__(self):
    return '<Network ' + ' '.join(('{}: {}'.format(item, self.__dict__[item]) for item in self.__dict__)) + '>'
    
  def __str__(self):
    return  '<class Network>' + '\n'+ ', '.join(('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__))

  def polymer(self, type, *args):
    print(args)
    if type == 'compose':
      if len(args) == 1:
        raise Exception('Polymer composition passed 1 chemical but expected 2')
      else:
        return concatenate(args)
    else:
      if len(args) > 1:
        raise Exception('Polymer decomposition passed ', len(args), ' chemicals but expected 1')
      else:
        return rand_split(args[0])

  def rearrangement(self, type, *args):
    if type == 'compose':
      if len(args) == 1:
        raise Exception('Rearrangement composition passed 1 chemical but expected 2')
      else:
        return shuffle(concatenate(args))
    else:
      if len(args) > 1:
        raise Exception('Rearrangement decomposition passed ', len(args), ' chemicals but expected 1')
      else:
        return rand_split(shuffle(args[0]))

  def aggregation(self, type, *args):
    if type == 'compose':
      if len(args) == 1:
        raise Exception('Aggregation composition passed 1 chemical but expected 2')
      else:
        return order(concatenate(args))
    else:
      if len(args) > 1:
        raise Exception('Aggregation decomposition passed ', len(args), ' chemical but expected 1')
      else:
        mol_A, mol_B = rand_split(shuffle(args[0]))
        return order(mol_A), order(mol_B)

  def new_reaction(self):
    i = random.randrange(3)
    # TODO
    DUMMY_CHEMICAL = '1010'
    DUMMY_CHEMICAL_1 = '11'
    DUMMY_CHEMICAL_2 = '00'
    if i == 0:
      if len(DUMMY_CHEMICAL) > 1:
        # return self.reactions.append(self.operator('decompose', DUMMY_CHEMICAL))  
        return print(self.operator('decompose', DUMMY_CHEMICAL))
        
    if i == 1:
      if len(DUMMY_CHEMICAL_1) + len(DUMMY_CHEMICAL_2) <= self.max_length:
        return print(self.operator('compose', DUMMY_CHEMICAL_1, DUMMY_CHEMICAL_2))
    
    return print(self.operator('decompose', self.operator('compose', DUMMY_CHEMICAL_1, DUMMY_CHEMICAL_2)))
    

  operator = polymer
  max_length = 4


test1 = Chemical('111', True)
test2 = Chemical('000', False)

