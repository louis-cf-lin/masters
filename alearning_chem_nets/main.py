import random, decimal

def concatenate(*args):
  return ''.join(*args)

def shuffle(chemical):
  return concatenate(random.sample(chemical, len(chemical)))

def order(chemical):
  return concatenate(sorted(chemical))

def rand_split(chemical):
  if len(chemical) == 2:
    rand_pos = 1
  else:
    rand_pos = random.randrange(1, len(chemical))
  return [chemical[:rand_pos], chemical[rand_pos:]]


def rand_float(lower, upper, digits=6):
  f = 10**digits
  return random.randint(lower*f, upper*f)/f

class Chemical:
  def __init__(self, formula, is_food=False):
    self.formula = formula
    self.potential = rand_float(0, 7.5)
    self.ic = rand_float(0, 2)
    if is_food:
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
    self.chemicals = [Chemical('111'), Chemical('00'), Chemical('01'), Chemical('101'), Chemical('1'), Chemical('0')] #TODO
    self.reactions = [] #TODO

  def __repr__(self):
    return '<Network ' + ' '.join(('{}: {}'.format(item, self.__dict__[item]) for item in self.__dict__)) + '>'
    
  def __str__(self):
    return  '<class Network>' + '\n'+ ', '.join(('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__))

  def polymer(self, type, *args):
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
    # rand_method = random.randrange(3)
    rand_method = 1

    if rand_method == 0:
      lhs = random.choice(self.chemicals).formula
      if len(lhs) > 1:
        rhs = self.operator('decompose', lhs)
        self.reactions.append(Reaction([lhs], rhs))
    else:
      lhs = (c.formula for c in random.sample(self.chemicals, 2))
      rhs = [self.operator('compose', lhs[0], lhs[1])]
      if (rand_method == 1) and (len(''.join(lhs)) <= self.max_length):
        self.reactions.append(Reaction(lhs, rhs))
      else:
        rhs = self.operator('decompose', rhs[0])
        self.reactions.append(Reaction(lhs, rhs))

    for rhs_chem in rhs:
      for chem in self.chemicals:
        print(rhs_chem, chem)
        if rhs_chem == chem.formula:
          console.log('found it!')
          break
    

  operator = polymer
  max_length = 4

test = Network()

test1 = Chemical('111', True)
test2 = Chemical('000', False)

