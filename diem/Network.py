from functools import reduce
import copy
import numpy as np
from collections import Counter

AGGREGATION = True

DT = 0.01
MUTATION_RATE = 0.1
DRAIN_RATE = 0.004

NETWORK_RNG = np.random.default_rng(814486224)

def add_noise(value, max):
  if NETWORK_RNG.random() < MUTATION_RATE:
    value += NETWORK_RNG.normal(loc=0, scale=max*MUTATION_RATE) 
    return max - abs(value % (2*max) - max)
  else:
    return value


class Chemical:

  N_GENES = 4

  INIT_POTENTIAL_MAX = 1
  INIT_INITIAL_CONC_MAX = 1
  INIT_DECAY_MAX = 1 # slower decay

  FORMULA_LEN_MAX = 4
  POTENTIAL_MAX = 7.5
  INITIAL_CONC_MAX = 1
  DECAY_MAX = 5
  
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

  def prep_update(self, sensor_reading=None):
    if sensor_reading is None:
      self.dconc = 0
    else:
      self.dconc = sensor_reading

  def update(self):
    self.conc =  min(100000.0, max(0.0, self.conc + self.dconc*DT))

  def mutate(self):
    self.potential = add_noise(self.potential, Chemical.POTENTIAL_MAX)
    self.initial_conc = add_noise(self.initial_conc, Chemical.INITIAL_CONC_MAX)
    self.decay = add_noise(self.decay, Chemical.DECAY_MAX)
    self.conc = self.initial_conc
    self.dconc = 0

class Reaction:
  
  INIT_FAV_RATE_MAX = 0.1
  FAV_RATE_MAX = 60
  
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
    return '{} → {}'.format(self.lhs, self.rhs)

  def __str__(self):
    return '{} → {}'.format(self.lhs, self.rhs)

  def prep_update(self):
    lhs_product = reduce(lambda x, y: x*y, [chemical.conc for chemical in self.lhs])
    rhs_product = reduce(lambda x, y: x*y, [chemical.conc for chemical in self.rhs])
    
    for chemical in self.lhs:
      chemical.dconc += rhs_product*self.backward - lhs_product*self.forward
    for chemical in self.rhs:
      chemical.dconc += lhs_product*self.forward - rhs_product*self.backward

    for chemical in self.lhs:
      chemical.dconc -= chemical.decay*chemical.conc

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

  INIT_CHEMICAL_LEN = 3
  N_INIT_CHEMICALS = 4
  N_INIT_REACTIONS = 20

  INPUT_LEFT = 0
  INPUT_RIGHT = 1
  OUTPUT_LEFT = 2
  OUTPUT_RIGHT = 3

  def __init__(self):
    self.chemicals = []
    while len(self.chemicals) < Network.N_INIT_CHEMICALS:
      formula = f'{NETWORK_RNG.integers(2**Network.INIT_CHEMICAL_LEN):03b}'
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
    self.chemicals[0].decay = NETWORK_RNG.random() * 5
    self.chemicals[1].decay = NETWORK_RNG.random() * 5

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
      i = NETWORK_RNG.integers(max(formula_len-Chemical.FORMULA_LEN_MAX, 1), min(formula_len,5))
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
  
  def get_outputs(self, left_reading, right_reading):
    for i, chemical in enumerate(self.chemicals):
      if i == Network.INPUT_LEFT:
        chemical.prep_update(left_reading)
      elif i == Network.INPUT_RIGHT:
        chemical.prep_update(right_reading)
      else:
        chemical.prep_update()
    for reaction in self.reactions:
      reaction.prep_update()
    
    for chemical in self.chemicals:
      chemical.update()
      chemical.hist.append(chemical.conc)
    
    return self.chemicals[Network.OUTPUT_LEFT].conc, self.chemicals[Network.OUTPUT_RIGHT].conc

  def mutate(self):
    for chemical in self.chemicals:
      chemical.mutate()
    for reaction in self.reactions:
      reaction.mutate()
    if NETWORK_RNG.random() < 5 * MUTATION_RATE:
      self.new_reaction()
    if NETWORK_RNG.random() < 5 * MUTATION_RATE:
      self.reactions.pop(NETWORK_RNG.integers(len(self.reactions)))
    if NETWORK_RNG.random() < MUTATION_RATE:
      i = NETWORK_RNG.choice(range(len(self.chemicals)), 2)
      self.chemicals[i[0]], self.chemicals[i[1]] = self.chemicals[i[1]], self.chemicals[i[0]]
  
  def print_derivs(self):
    derivs = {}

    for chemical in self.chemicals:
      derivs[chemical.formula] = f"-{chemical.decay:.2f}"

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
  copied = net.deep_copy()

  print(net == copied)