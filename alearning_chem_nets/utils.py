import random, math, params, warnings
import numpy as np
from functools import reduce
from operator import mul

def concatenate(*args):
  return ''.join(*args)

def shuffle(chemical):
  return concatenate(random.sample(chemical, len(chemical)))

def order(chemical):
  return concatenate(sorted(chemical))

def rand_split(chemical):
  length = len(chemical)
  if length > params.max_length:
    pos = random.randint(length - params.max_length, params.max_length)
  else:
    pos = random.randrange(1, length)
  return [chemical[:pos], chemical[pos:]]

def rand_float(lower, upper, digits=6):
  f = 10**digits
  return random.randint(lower*f, upper*f)/f

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

def delta_reaction(reaction):
  #TODO: check rate constants are correct
  lhs_potential = sum([lhs_chem.potential for lhs_chem in reaction.lhs])
  rhs_potential = sum([rhs_chem.potential for rhs_chem in reaction.rhs])

  if lhs_potential > rhs_potential:
    lhs_product = reduce(mul, [lhs_chem.conc for lhs_chem in reaction.lhs]) * reaction.frc
    with warnings.catch_warnings():
      warnings.filterwarnings('error')
      try:
        rhs_product = reduce(mul, [rhs_chem.conc for rhs_chem in reaction.rhs]) * math.exp(- (-np.log(reaction.frc) + (lhs_potential - rhs_potential)))
      except Warning as e:
        raise Exception(e)
  else:
    with warnings.catch_warnings():
      warnings.filterwarnings('error')
      try:
        lhs_product = reduce(mul, [lhs_chem.conc for lhs_chem in reaction.lhs]) *  math.exp(- (-np.log(reaction.frc) + (rhs_potential - lhs_potential)))
      except Warning as e:
        raise Exception(e)
    rhs_product = reduce(mul, [rhs_chem.conc for rhs_chem in reaction.rhs]) * reaction.frc

  all_chemicals = reaction.lhs + reaction.rhs
  lhs_len = len(reaction.lhs)
  for i, chemical in enumerate(all_chemicals):
    if i < lhs_len:
      chemical.delta += rhs_product - lhs_product
    else:
      chemical.delta += lhs_product - rhs_product

  return

def delta_chemical(chemical):
  chemical.delta += -chemical.decay*chemical.conc + chemical.inflow*chemical.is_food
  return

def compute_step(chemical):
  chemical.conc += chemical.delta * params.dt
  chemical.conc = min(chemical.conc, 5)
  chemical.delta = 0
  return

def add_gauss(value, sd, inclusive_range):
  noise = random.gauss(0, sd)
  new_value = value + noise
  if new_value < inclusive_range[0]:
    return inclusive_range[0] + (inclusive_range[0] - new_value)
  elif new_value > inclusive_range[1]:
    return inclusive_range[1] - (new_value - inclusive_range[1])

  if new_value == 0:
      raise Exception('0 value found')

  return new_value

def clocked():
  
  interval = 100
  ticks = math.floor(params.task_duration/interval)

  targets = []

  for i in range(1, ticks):
    if random.random() < 0.5:
      targets.append(i*interval - 1)

  if len(targets) < 1:
    targets = clocked()

  return targets

def evaluate(network, targets, env):
  output = [None] * params.task_duration

  target_index = 0
  next_target = 0
  number_of_targets = len(targets)

  for chemical in network.chemicals:
    chemical.conc = chemical.initial_conc

  for k in range(params.task_duration):

    network.simulate()

    if next_target < number_of_targets:
      if k == targets[next_target]:
        network.chemicals[0].conc = 3
      elif k == (targets[next_target]+20):
        network.chemicals[1].conc = 3
        next_target += 1
    else:
      break
    
    output[k] = network.chemicals[2].conc

  error = 0

  if env == 'associated':
    for target in targets:
      for i in range(20):
        error += (output[i+target+1] - 3)**2
    return -error/(20*len(targets))

  if env == 'unassociated':
    for target in targets:
      for i in range(20):
        error += (output[i+target+1])**2
    return -error/(20*len(targets))