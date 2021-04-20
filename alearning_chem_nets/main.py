import random, decimal, numpy
from collections import OrderedDict

max_length = 4

def concatenate(*args):
  return ''.join(*args)

def shuffle(chemical):
  return concatenate(random.sample(chemical, len(chemical)))

def order(chemical):
  return concatenate(sorted(chemical))

def rand_split(chemical):
  length = len(chemical)
  if length > max_length:
    pos = random.randint(length - max_length, max_length)
  else:
    pos = random.randrange(1, length)
  return [chemical[:pos], chemical[pos:]]

def rand_float(lower, upper, digits=6):
  f = 10**digits
  return random.randint(lower*f, upper*f)/f

def solve_delta(reaction):
  #TODO: replace with actual rates
  DUMMY_FORWARD_RATE = 1
  DUMMY_BACKWARD_RATE = 1
  lhs_product = numpy.prod([lhs_chem.conc for lhs_chem in reaction.lhs]) * DUMMY_FORWARD_RATE
  rhs_product = numpy.prod([rhs_chem.conc for rhs_chem in reaction.rhs]) * DUMMY_BACKWARD_RATE

  all_chemicals = reaction.lhs + reaction.rhs

  delta = [None] * len(all_chemicals)
  for i, chemical in enumerate(all_chemicals):
    if i < len(reaction.lhs):
      delta[i] = rhs_product - lhs_product - chemical.decay*chemical.conc + chemical.inflow
    else:
      delta[i] = lhs_product - rhs_product - chemical.decay*chemical.conc + chemical.inflow

  return delta

class Chemical:
  def __init__(self, formula=None, is_food=False):
    if formula:
      self.formula = formula
    else:
      self.formula = format(random.randint(0, 2**3), '03b')
    self.potential = rand_float(0, 7.5)
    self.conc = rand_float(0, 2)
    if is_food:
      self.inflow = rand_float(0, 1)
    else:
      self.inflow = 0
    self.decay = rand_float(0, 1)
  
  def __repr__(self):
    return '\n<Chemical ' + ' '.join(('{}: {}'.format(item, self.__dict__[item]) for item in self.__dict__)) + '>'
    
  def __str__(self):
    return  '<class Chemical>' + '\n'+ ', '.join(('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__))

class Reaction:
  def __init__(self, lhs, rhs):
    self.lhs = lhs
    self.rhs = rhs
    self.frc = rand_float(0, 0.1)
    self.system = []

  def __repr__(self):
    return '\n<Reaction\n' + '\n '.join(('{}: {}'.format(item, self.__dict__[item]) for item in self.__dict__)) + '>'
    
  def __str__(self):
    return  '<class Reaction>' + '\n'+ ', '.join(('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__))

class Network:

  def __init__(self, num_of_seeds=4, seed_length=3):
    seeds = random.sample(range(2**seed_length), num_of_seeds)
    self.chemicals = [Chemical(format(seed, '03b')) for seed in seeds]
    self.reactions = []
    for _ in range(20):
      self.new_reaction()
    random.shuffle(self.chemicals)

  def __repr__(self):
    return '<Network ' + ' '.join(('{}: {}'.format(item, self.__dict__[item]) for item in self.__dict__)) + '>'
    
  def __str__(self):
    return  '<class Network' + '\n'+ ', \n'.join(('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__)) + '>'

  def polymer(self, type, *args):
    if type == 'compose':
      if len(args) == 1:
        raise Exception('Polymer composition passed 1 chemical but expected 2')
      else:
        return [concatenate(args)]
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
    method = random.randrange(3)

    if method == 0:
      lhs = random.choices(self.chemicals)
      if len(lhs[0].formula) > 1:
        rhs_formula = self.operator('decompose', lhs[0].formula)
      else:
        return
    else:
      lhs = random.choices(self.chemicals, k=2)
      rhs_formula = self.operator('compose', lhs[0].formula, lhs[1].formula)
      if (method == 1) and (len(''.join([lhs_chem.formula for lhs_chem in lhs])) <= max_length):
        pass
      else:
        rhs_formula = self.operator('decompose', rhs_formula[0])

    rhs = []

    for formula in rhs_formula:
      for chem in self.chemicals:
        if formula == chem.formula:
          rhs.append(chem)
          break
      else:
        new_chem = Chemical(formula)
        self.chemicals.append(new_chem)
        rhs.append(new_chem)

    self.reactions.append(Reaction(lhs, rhs))

  def simulate(self):
    self.chemicals

  operator = polymer

test = Network()


print(test)
