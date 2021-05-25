import random
from simulate import simulate_main
from utils import polymer
import matplotlib.pyplot as plt 


class Chemical:
  def __init__(self, formula, potential=None, initial_conc=None, decay=None, inflow=None):

    if potential is None:
      potential = random.uniform(0, 7.5)
    if initial_conc is None:
      initial_conc = random.uniform(0, 2)
    if decay is None:
      decay = random.uniform(0, 1)
    if inflow is None:
      inflow = random.uniform(0, 1)

    self.formula = formula
    self.potential = potential
    self.initial_conc = initial_conc
    self.inflow = inflow
    self.decay = decay
    self.conc = 0
    self.delta = 0
  
  def __repr__(self):
    return '\n<Chemical ' + ', '.join(('{}: {}'.format(item, self.__dict__[item]) for item in self.__dict__)) + '>'
    
  def __str__(self):
    return  '<class Chemical>' + '\n'+ ', '.join(('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__))
    
class Reaction:
  # forward always favoured (swap if necessary)
  def __init__(self, lhs, rhs, forward=None, backward=None):

    if forward is None:
      forward = random.uniform(0, 0.1)
      if sum(lhs_chem.potential for lhs_chem in lhs) < sum(rhs_chem.potential for rhs_chem in rhs):
        lhs, rhs = rhs, lhs
    if backward is None:
      backward = forward/2

    self.lhs = lhs
    self.rhs = rhs
    self.forward = forward
    self.backward = backward

  def __repr__(self):
    return '\n<Reaction ' + ' + '.join(chem.formula for chem in self.lhs) + ' -> ' + ' + '.join(chem.formula for chem in self.rhs)  + ' >'
    return '\n<Reaction\n' + '\n '.join(('hello' for item in self.__dict__)) + ' >'

  def __str__(self):
    return  '<class Reaction>' + '\n'+ ', '.join(('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__))

class Network:
  def __init__(self, chemicals=None, reactions=None, formula_length=3, num_of_seeds=4):
    if chemicals is None:
      # random distinct binary formulae
      seeds = random.sample(range(2**formula_length), num_of_seeds)
      chemicals = [Chemical(formula=format(seed, '03b')) for seed in seeds]
    self.chemicals = chemicals

    if reactions is None:
      self.reactions = []
      for _ in range(20):
        self.add_reaction()
    else:
      self.reactions = reactions

    self.fitness = 0

  def __repr__(self):
    return '<Network ' + ' '.join(('{}: {}'.format(item, self.__dict__[item]) for item in self.__dict__)) + '>'
    
  def __str__(self):
    return  '<class Network' + '\n'+ ', \n'.join(('{} = {}'.format(item, self.__dict__[item]) for item in self.__dict__)) + '>'
  
  def evaluate(self, duration, boluses, delay=20, plot=False):
    # execute one simulation 
    stimulus, control, output = simulate_main(self, duration, boluses)
    
    # evaluate total error
    error = 0
    for bolus in boluses:
      for i in range(delay + 1):
        error += (output[bolus+i] - 1)**2

    # calculate average
    self.fitness = -error/(len(boluses)*delay)
    print(self.fitness)

    if plot:
      plt.plot(stimulus, color='blue', label='Stimulus')
      plt.plot(control, color='green', label='Control')
      plt.plot(output, color='black', label='Output')
      plt.legend()
      plt.xlabel('Iteration')
      plt.ylabel('Concentration')
      plt.show()

  def add_reaction(self, max_length=4):
    # pick a random method
    method = random.randrange(3)

    if method == 0:
      # method 1: decompose
      lhs = random.choices(self.chemicals)
      if len(lhs[0].formula) > 1:
        rhs_formula = polymer('decompose', lhs[0].formula)
      else:
        return
    else:
      lhs = random.choices(self.chemicals, k=2)
      rhs_formula = polymer('compose', lhs[0].formula, lhs[1].formula)
      if (method == 1) and (len(''.join([lhs_chem.formula for lhs_chem in lhs])) <= max_length):
        # method 2: compose
        pass
      else:
        # method 3: compose and decompose
        rhs_formula = polymer('decompose', rhs_formula[0])

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