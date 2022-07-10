from functools import reduce
import numpy as np
import matplotlib.pyplot as plt 

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

  INIT_POTENTIAL_MAX = 7.5
  INIT_INITIAL_CONC_MAX = 2
  INIT_INFLOW_MAX = 1
  INIT_DECAY_MAX = 1

  FORMULA_LEN_MAX = 4
  POTENTIAL_MAX = 7.5
  INITIAL_CONC_MAX = 5
  INFLOW_MAX = 5
  DECAY_MAX = 10
  
  def __init__(self, formula):
    self.formula = formula
    self.potential = NETWORK_RNG.random() * Chemical.INIT_POTENTIAL_MAX
    self.initial_conc = NETWORK_RNG.random() * Chemical.INIT_INITIAL_CONC_MAX
    self.conc = self.initial_conc
    self.dconc = 0
    self.inflow = NETWORK_RNG.random() * Chemical.INIT_INFLOW_MAX
    self.decay = NETWORK_RNG.random() * Chemical.INIT_DECAY_MAX

    self.hist = [self.initial_conc]
  
  def __repr__(self):
    return self.formula

  def __str__(self):
    return self.formula    

  def prep_update(self):
    self.dconc = 0

  def update(self):
    self.conc += self.dconc*DT

  def mutate(self):
    self.potential = add_noise(self.potential, Chemical.POTENTIAL_MAX)
    self.initial_conc = add_noise(self.initial_conc, Chemical.INITIAL_CONC_MAX)
    self.conc = self.initial_conc
    self.inflow = add_noise(self.inflow, Chemical.INFLOW_MAX)
    self.decay = add_noise(self.decay, Chemical.DECAY_MAX)

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
      chemical.dconc += chemical.decay*chemical.conc

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
  N_INIT_CHEMICALS = 2
  N_INIT_REACTIONS = 20

  INPUT_1 = 0
  INPUT_2 = 1
  OUTPUT = 2

  def __init__(self, chemicals=None, reactions=None):
    if chemicals is None:
      self.chemicals = []
      while len(self.chemicals) <= Network.N_INIT_CHEMICALS:
        formula = f'{NETWORK_RNG.integers(2**Network.INIT_CHEMICAL_LEN):03b}'
        if AGGREGATION:
          formula = ''.join(sorted(formula))
        for chem in self.chemicals:
          if chem.formula == formula:
            break
        else:
          self.chemicals.append(Chemical(formula=formula))
    else:
      self.chemicals = chemicals
  
    if reactions is None:
      self.reactions = []
      for _ in range(Network.N_INIT_REACTIONS):
        self.new_reaction()
    else:
      self.reactions = reactions

    NETWORK_RNG.shuffle(self.chemicals)

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
    
    return self.reactions.append(Reaction(lhs, np.array(rhs)))
  
  def step(self):
    for chemical in self.chemicals:
      chemical.prep_update()
    for reaction in self.reactions:
      reaction.prep_update()

    # TODO update battery and check if still alive
    # self.chemicals[Network.BATTERY_1].dconc = -DRAIN_RATE
    # self.chemicals[Network.BATTERY_2].dconc = -DRAIN_RATE
    
    for chemical in self.chemicals:
      chemical.update()
      chemical.hist.append(chemical.conc)

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

net = Network()


for i in range(200):
  net.step()


for chemical in net.chemicals:
  plt.plot(chemical.hist)

plt.ylim(0,5)

plt.show()