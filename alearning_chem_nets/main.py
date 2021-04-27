import random, decimal, math, pickle, copy
import numpy as np
from operator import mul
from functools import reduce
import matplotlib.pyplot as plt

random.seed(0)
max_length = 4
dt = 0.01
sigma = 0.1 # mutation rate

potential_range = [0, 7.5]
conc_range = [0, 5]
inflow_range = [0, 5]
decay_range = [0, 10]
frc_range = [0, 60]

potential_sd = sigma * abs(potential_range[1] - potential_range[0])
conc_sd = sigma * abs(conc_range[1] - conc_range[0])
inflow_sd = sigma * abs(inflow_range[1] - inflow_range[0])
decay_sd = sigma * abs(decay_range[1] - decay_range[0])
frc_sd = sigma * abs(frc_range[1] - frc_range[0])

prob_new_reaction = sigma * 5
prob_del_reaction = sigma * 5

task_duration = 1100


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
    rhs_product = reduce(mul, [rhs_chem.conc for rhs_chem in reaction.rhs]) * (reaction.frc + lhs_potential - rhs_potential)
  else:
    lhs_product = reduce(mul, [lhs_chem.conc for lhs_chem in reaction.lhs]) * (reaction.frc + rhs_potential - lhs_potential)
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
  chemical.conc += chemical.delta * dt
  chemical.conc = min(chemical.conc, 5)
  chemical.delta = 0
  return

def add_gauss(value, sd, range):
  noise = value + random.gauss(0, sd)
  new_value = value + noise
  if new_value < range[0]:
    return new_value + (range[0] - new_value)
  elif new_value > range[1]:
    return new_value - (new_value - range[1])

  return new_value

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

  operator = polymer

  def __init__(self, num_of_seeds=4, seed_length=3):
    seeds = random.sample(range(2**seed_length), num_of_seeds)
    self.chemicals = [Chemical(format(seed, '03b')) for seed in seeds]
    self.reactions = []
    for _ in range(20):
      self.new_reaction()
    random.shuffle(self.chemicals)
    self.update_chemicals(True)

  def __repr__(self):
    return '<Network ' + ' '.join(('{}: {}'.format(item, self.__dict__[item]) for item in self.__dict__)) + '>'
    
  def __str__(self):
    return  '<class Network' + '\n'+ ', \n'.join(('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__)) + '>'

  def update_chemicals(self, value):
    self.chemicals[0].is_stimulus = value
    self.chemicals[1].is_control = value
    self.chemicals[2].is_output = value
    self.chemicals[3].is_food = value

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

    return self.reactions.append(Reaction(lhs, rhs))

  def mutate(self):

    for chemical in self.chemicals:
      chemical.potential = add_gauss(chemical.potential, potential_sd, potential_range)
      chemical.conc = add_gauss(chemical.conc, conc_sd, conc_range)
      chemical.inflow = add_gauss(chemical.inflow, inflow_sd, inflow_range)
      chemical.decay = add_gauss(chemical.decay, decay_sd, decay_range)

    if random.random() < prob_del_reaction:
      self.reactions.pop(random.randrange(0, len(self.reactions)))

    for reaction in self.reactions:
      reaction.frc = add_gauss(reaction.frc, frc_sd, frc_range)

    if random.random() < prob_new_reaction:
      self.new_reaction()

    if random.random() < sigma:
      self.update_chemicals(False)
      pos_arr = random.sample(range(len(self.chemicals)), k=2)
      self.chemicals[pos_arr[0]], self.chemicals[pos_arr[1]] = self.chemicals[pos_arr[1]], self.chemicals[pos_arr[0]]
      self.update_chemicals(True)

    return

  def simulate(self):
    for reaction in self.reactions:
      delta_reaction(reaction)
    for chemical in self.chemicals:
      delta_chemical(chemical)
      compute_step(chemical)
    
    return

def clocked():
  
  interval = 100
  ticks = math.floor(task_duration/interval)

  targets = []

  for i in range(1, ticks):
    if random.random() < 0.5:
      targets.append(i*interval - 1)

  if len(targets) < 1:
    targets = clocked()

  return targets

def evaluate(network, targets, env):
  output = [None] * task_duration

  next_target = 0
  number_of_targets = len(targets)
  for k in range(task_duration):
    if next_target < number_of_targets:
      if k == targets[next_target]:
        network.chemicals[0].conc = 3
      elif k == (targets[next_target]+20):
        network.chemicals[1].conc = 3
        next_target += 0
    else:
      break
    
    network.simulate()
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

class Population:
  def __init__(self, size):
    self.networks = [None] * size
    for i in range(size):
      self.networks[i] = Network()

  def compete(self, protocol):
    competitors = random.sample(self.networks, 2)

    fitness_a = 0
    fitness_b = 0
    for _ in range(10):
      targets = protocol()
      fitness_a += evaluate(competitors[0], targets, 'associated')
      fitness_a += evaluate(competitors[0], targets, 'unassociated')
      fitness_b += evaluate(competitors[1], targets, 'associated')
      fitness_b += evaluate(competitors[1], targets, 'unassociated')

    if fitness_a > fitness_b:
      self.networks.remove(competitors[1])
      self.networks.append(copy.deepcopy(competitors[0]))
    else:
      self.networks.remove(competitors[0])
      self.networks.append(copy.deepcopy(competitors[1]))

    self.networks[-1].mutate()

def main():

  population = Population(10)

  task = clocked()
  error_before = 0
  for network in population.networks:
    error_before += evaluate(network, task, 'associated')
    error_before += evaluate(network, task, 'unassociated')

  print(error_before)

  for _ in range(50):
    population.compete(clocked)
  

  f = open('store.pckl', 'wb')
  pickle.dump(population, f)
  f.close()

  # f = open('store.pckl', 'rb')
  # population = pickle.load(f)
  # f.close()

  print(population)

  error_after = 0
  for network in population.networks:
    error_after += evaluate(network, task, 'associated')
    error_after += evaluate(network, task, 'unassociated')

  print(error_after)

  # fig1, ax1 = plt.subplots()
  # ax1.plot(a_1)
  # plt.show()

  # output_b = clocked(test_b)

if __name__ == '__main__':
  main()


