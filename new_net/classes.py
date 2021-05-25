import random

class Chemical:
  def __init__(self, formula, potential=random.uniform(0, 0.1), initial_conc=random.uniform(0, 2), decay=random.uniform(0, 1), inflow=random.uniform(0, 1)):
    self.formula = formula
    self.potential = potential
    self.initial_conc = initial_conc
    self.inflow = inflow
    self.decay = decay
    self.conc = 0
    self.delta = 0
    
class Reaction:
  # forward always favoured (swap if necessary)
  def __init__(self, lhs, rhs, forward=0, backward=0):
    self.lhs = lhs
    self.rhs = rhs
    self.forward = forward
    self.backward = backward

class Network:
  def __init__(self, chemicals=None, reactions=None, seed_length=3, num_of_seeds=4):
    if chemicals is None:
      seeds = random.sample(range(2**seed_length), num_of_seeds)
      self.chemicals = [Chemical(formula=format(seed, '03b')) for seed in seeds]
      random.shuffle(self.chemicals)
      self.set_roles(True)
    else:
      self.chemicals = chemicals

    if reactions is None:
      for _ in range(20):
        self.new_reaction()
    else:
      self.reactions = reactions

    self.fitness = 0
  
  def set_roles(self, bool):
    self.chemicals[0].is_stimulus = bool
    self.chemicals[1].is_control = bool
    self.chemicals[2].is_output = bool
    self.chemicals[3].is_food = bool

  # def new_reaction(self):
  #   method = random.randrange(3)

  #   if method == 0:
  #     lhs = random.choices(self.chemicals)
  #     if len(lhs[0].formula) > 1:
  #       rhs_formula = self.operator('decompose', lhs[0].formula)
  #     else:
  #       return
  #   else:
  #     lhs = random.choices(self.chemicals, k=2)
  #     rhs_formula = self.operator('compose', lhs[0].formula, lhs[1].formula)
  #     if (method == 1) and (len(''.join([lhs_chem.formula for lhs_chem in lhs])) <= params.max_length):
  #       pass
  #     else:
  #       rhs_formula = self.operator('decompose', rhs_formula[0])

  #   rhs = [] 
  #   for formula in rhs_formula:
  #     for chem in self.chemicals:
  #       if formula == chem.formula:
  #         rhs.append(chem)
  #         break
  #     else:
  #       new_chem = Chemical(formula)
  #       self.chemicals.append(new_chem)
  #       rhs.append(new_chem)

  #   self.reactions.append(Reaction(lhs, rhs))