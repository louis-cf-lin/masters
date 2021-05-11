import random, params
from Chemical import Chemical
from Reaction import Reaction
from utils import polymer, add_gauss, delta_reaction, delta_chemical, compute_step

class Network:

  operator = polymer

  def __init__(self, num_of_seeds=4, seed_length=3, operator=polymer):
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
      if (method == 1) and (len(''.join([lhs_chem.formula for lhs_chem in lhs])) <= params.max_length):
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

  def simulate(self):
    for reaction in self.reactions:
      delta_reaction(reaction)
    for chemical in self.chemicals:
      delta_chemical(chemical)
      compute_step(chemical)
    
    return