from functools import reduce
from Sides import Sides
from collections import Counter
import copy
import numpy as np
from Env import EnvObjectTypes
from globals import DT, AGGREGATION, MUTATION_RATE


NETWORK_RNG = np.random.default_rng(814486224)

def rand_formula(min_len = 4, max_len = 4):
  formula = ''
  length = NETWORK_RNG.integers(min_len, max_len + 1)
  for _ in range(length):
    formula += str(NETWORK_RNG.integers(2))
  return formula

def add_noise(value, max):
  if NETWORK_RNG.random() < MUTATION_RATE:
    return max - abs((value + NETWORK_RNG.normal(loc=0, scale=max*MUTATION_RATE)) % (2*max) - max)
  else:
    return value


class Chemical:

  N_GENES = 4

  INIT_POTENTIAL_MAX = 7.5
  INIT_INITIAL_CONC_MAX = 2.0
  INIT_DECAY_MAX = 1.0

  FORMULA_LEN_MAX = 4
  POTENTIAL_MAX = 7.5
  INITIAL_CONC_MAX = 5.0
  DECAY_MAX = 10.0
  
  def __init__(self, formula):
    self.formula = formula
    self.potential = NETWORK_RNG.random() * Chemical.INIT_POTENTIAL_MAX
    self.initial_conc = NETWORK_RNG.random() * Chemical.INIT_INITIAL_CONC_MAX
    self.conc = self.initial_conc
    self.dconc = 0
    self.decay = NETWORK_RNG.random() * Chemical.INIT_DECAY_MAX

    self.hist = [self.initial_conc]
  
  def __eq__(self, other):
    return self.formula == other.formula and self.potential == other.potential and self.initial_conc == other.initial_conc and self.conc == other.conc and self.dconc == other.dconc and self.decay == other.decay and np.array_equal(self.hist, other.hist)
  
  def __repr__(self):
    return self.formula

  def __str__(self):
    return self.formula    

  def prep_update(self, reading = None):
    self.dconc = -self.decay * self.conc
    if not reading == None:
      self.dconc += reading

  def update(self):
    if (self.dconc > 100 or self.dconc < -100):
      print('pause')
    self.conc = max(0.0, self.conc + self.dconc * DT)
    self.hist.append(self.conc)    

  def mutate(self):
    self.potential = add_noise(self.potential, Chemical.POTENTIAL_MAX)
    self.initial_conc = add_noise(self.initial_conc, Chemical.INITIAL_CONC_MAX)
    self.decay = add_noise(self.decay, Chemical.DECAY_MAX)
    self.conc = self.initial_conc
    self.dconc = 0

class Reaction:
  
  INIT_FAV_RATE_MAX = 0.1
  FAV_RATE_MAX = 60.0
  
  def __init__(self, lhs, rhs):
    self.lhs = lhs
    self.rhs = rhs
    self.fav_rate = NETWORK_RNG.random() * Reaction.INIT_FAV_RATE_MAX

    # unfavoured rate = favoured rate * e^(-R+P)
    mu_lhs = sum([lhs.potential for lhs in self.lhs])
    mu_rhs = sum([rhs.potential for rhs in self.rhs])
    if mu_lhs > mu_rhs:
      self.forward = self.fav_rate
      self.backward = self.fav_rate * (np.e ** (-mu_lhs+mu_rhs))
    else:
      self.backward = self.fav_rate
      self.forward = self.fav_rate * (np.e ** (-mu_rhs+mu_lhs))
  
  def __eq__(self, other):
    return np.array_equal(self.lhs, other.lhs) and np.array_equal(self.rhs, other.rhs) and self.forward == other.forward and self.backward == other.backward
  
  def __repr__(self):
    return '+'.join([f'[{chem.formula}]' for chem in self.lhs]) + '↔' + '+'.join([f'[{chem.formula}]' for chem in self.rhs])

  def __str__(self):
    return '+'.join([f'[{chem.formula}]' for chem in self.lhs]) + '↔' + '+'.join([f'[{chem.formula}]' for chem in self.rhs])
  
  def prep_update(self):
    lhs_product = reduce(lambda x, y: x*y, [chemical.conc for chemical in self.lhs])
    rhs_product = reduce(lambda x, y: x*y, [chemical.conc for chemical in self.rhs])
    
    for chemical in self.lhs:
      chemical.dconc += rhs_product*self.backward - lhs_product*self.forward
    for chemical in self.rhs:
      chemical.dconc += lhs_product*self.forward - rhs_product*self.backward

  def mutate(self):
    self.fav_rate = add_noise(self.fav_rate, Reaction.FAV_RATE_MAX)

    mu_lhs = sum([lhs.potential for lhs in self.lhs])
    mu_rhs = sum([rhs.potential for rhs in self.rhs])
    if mu_lhs > mu_rhs:
      self.forward = self.fav_rate
      self.backward = self.fav_rate * (np.e ** (-mu_lhs+mu_rhs))
    else:
      self.backward = self.fav_rate
      self.forward = self.fav_rate * (np.e ** (-mu_rhs+mu_lhs))


class Network:

  N_INIT_CHEMICALS = 6
  N_INIT_REACTIONS = 6

  OUTPUT_LEFT = 0
  OUTPUT_RIGHT = 1
  FOOD_LEFT = 2
  FOOD_RIGHT = 3
  WATER_LEFT = 4
  WATER_RIGHT = 5

  def __init__(self):
    self.chemicals = []
    while len(self.chemicals) < Network.N_INIT_CHEMICALS:
      formula = rand_formula(min_len = 1)
      if AGGREGATION:
        formula = ''.join(sorted(formula))
      for chem in self.chemicals:
        if chem.formula == formula:
          break
      else:
        self.chemicals.append(Chemical(formula=formula))

    self.reactions = []
    for _ in range(Network.N_INIT_REACTIONS):
      self.new_reaction()

    NETWORK_RNG.shuffle(self.chemicals)

  def __eq__(self, other):
    return np.array_equal(self.chemicals, other.chemicals) and np.array_equal(self.reactions, other.reactions)

  def deep_copy(self):
    deep_copy = copy.deepcopy(self)
    for chem in deep_copy.chemicals:
      chem.conc = chem.initial_conc
      chem.dconc = 0
      chem.hist = [chem.initial_conc]
    return deep_copy

  def __repr__(self):
    return ' '.join([repr(chemical) for chemical in self.chemicals]) + '\n' + '\n'.join([repr(reaction) for reaction in self.reactions])

  def __str__(self):
    return ' '.join([repr(chemical) for chemical in self.chemicals]) + '\n' + '\n'.join([repr(reaction) for reaction in self.reactions])

  def new_reaction(self):

    def decompose(formula):
      formula_len = len(formula)
      if AGGREGATION:
        formula = ''.join(NETWORK_RNG.permutation(list(formula)))
      i = NETWORK_RNG.integers(max(formula_len-Chemical.FORMULA_LEN_MAX, 1), min(formula_len, Chemical.FORMULA_LEN_MAX+1))
      return [formula[:i], formula[i:]]

    def compose(formulas):
      return [''.join(formulas)]
    
    method = NETWORK_RNG.integers(3)
    if method == 0:
      lhs = NETWORK_RNG.choice(self.chemicals, size=1)
      if len(lhs[0].formula) > 1:
        rhs_formulas = decompose(lhs[0].formula)
      else:
        return
    else:
      lhs = NETWORK_RNG.choice(self.chemicals, size=2)
      rhs_formulas = compose([chem.formula for chem in lhs])
      if len(rhs_formulas[0]) > Chemical.FORMULA_LEN_MAX or method == 2:
        rhs_formulas = decompose(rhs_formulas[0])
    
    if AGGREGATION:
      rhs_formulas = [''.join(sorted(formula)) for formula in rhs_formulas]
    rhs = []
    for formula in rhs_formulas:
      for chem in self.chemicals:
        if formula == chem.formula:
          rhs.append(chem)
          break
      else:
        new_chem = Chemical(formula)
        self.chemicals.append(new_chem)
        rhs.append(new_chem)
    
    if not (Counter([lhs_chem.formula for lhs_chem in lhs]) == Counter([rhs_chem.formula for rhs_chem in rhs])):
      self.reactions.append(Reaction(lhs, np.array(rhs)))
    return 
  
  def get_outputs(self, readings):
    # set decay
    for chemical in self.chemicals:
      chemical.prep_update()

    # TODO uncomment if using natural dconc for inputs
    # add sensor inputs
    # for type in EnvObjectTypes:
    #   for side in Sides:
    #     self.chemicals[getattr(Network, f'{type.name}_{side.name}')].prep_update(readings[side.value][type.value])

    # set reaction changes
    for reaction in self.reactions:
      reaction.prep_update()
    # update chemicals
    for chemical in self.chemicals:
      chemical.update()
    
    # TODO uncomment if using natural dconc for inputs
    for type in EnvObjectTypes:
      for side in Sides:
        self.chemicals[getattr(Network, f'{type.name}_{side.name}')].conc = readings[side.value][type.value] * 2
    

    
    return self.chemicals[Network.OUTPUT_LEFT].conc, self.chemicals[Network.OUTPUT_RIGHT].conc

  def mutate(self):
    for chemical in self.chemicals:
      chemical.mutate()
    for reaction in self.reactions:
      reaction.mutate()
    if NETWORK_RNG.random() < 5 * MUTATION_RATE:
      self.new_reaction()
    if NETWORK_RNG.random() < 5 * MUTATION_RATE:
      if not len(self.reactions):
        self.new_reaction()
      else:
        self.reactions.pop(NETWORK_RNG.integers(len(self.reactions)))
    if NETWORK_RNG.random() < MUTATION_RATE:
      i = NETWORK_RNG.choice(range(len(self.chemicals)), 2)
      self.chemicals[i[0]], self.chemicals[i[1]] = self.chemicals[i[1]], self.chemicals[i[0]]
  
  def print_derivs(self):
    derivs = {}

    for chemical in self.chemicals:
      derivs[chemical.formula] = f"-{chemical.decay:.2f}[{chemical.formula}]"

    for reaction in self.reactions:
      for chem in reaction.lhs:
        derivs[chem.formula] += f" + {reaction.backward:.2f}"
        for rhs_chem in reaction.rhs:
          derivs[chem.formula] += f"[{rhs_chem}]"
        
        derivs[chem.formula] += f" - {reaction.forward:.2f}"
        for lhs_chem in reaction.lhs:
          derivs[chem.formula] += f"[{lhs_chem}]"

      for chem in reaction.rhs:
        derivs[chem.formula] += f" + {reaction.forward:.2f}"
        for lhs_chem in reaction.lhs:
          derivs[chem.formula] += f"[{lhs_chem}]"
        
        derivs[chem.formula] += f" - {reaction.backward:.2f}"
        for rhs_chem in reaction.rhs:
          derivs[chem.formula] += f"[{rhs_chem}]"

    for chemical, exp in derivs.items():
      print(f"{chemical}: {exp}")


if __name__ == '__main__':
  net = Network()
  print(net)