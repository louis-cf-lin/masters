from functools import reduce
import matplotlib.pyplot as plt

class Network:
  def __init__(self, reactions, chemicals):
    self.reactions = reactions
    self.chemicals = chemicals

class Reaction:
  def __init__(self, lhs, rhs, forward, backward):
    self.lhs = lhs
    self.rhs = rhs
    self.forward = forward
    self.backward = backward

class Chemical:
  def __init__(self, formula, initial_conc, decay, inflow=0, stimulus=False, control=False, output=False):
    self.formula = formula
    self.conc = initial_conc
    self.decay = decay
    self.inflow = inflow
    self.stimulus = stimulus
    self.control = control
    self.output = output
    self.delta = 0

chem_001 = Chemical('001', 0.004218, 2.721381, stimulus=True)
chem_011 = Chemical('011', 0.155827, 3.738387, control=True)
chem_000 = Chemical('000', 1.617242, 3.626139)
chem_0 = Chemical('0', 4.278178, 4.204123)
chem_01 = Chemical('01', 0.045266, 0.873102, output=True)
chem_00 = Chemical('00', 0.866823, 1.552885)
chem_0001 = Chemical('0001', 0.628683, 1.969112)
chem_1 = Chemical('1', 1.349662, 5.946280)
chem_0011 = Chemical('0011', 0.669255, 3.171469, inflow=0.372868)
chem_0111 = Chemical('0111', 0.283833, 0.047865)
chem_11 = Chemical('11', 0.255579, 3.106958)
chem_111 = Chemical('111', 1.008871, 0.217617)

chemicals = [chem_001, chem_011, chem_01, chem_000, chem_0, chem_00, chem_0001, chem_1, chem_0011, chem_0111, chem_11, chem_111]

reactions = [Reaction([chem_000], [chem_0, chem_00], 36.145961, 0.718663), Reaction([chem_000, chem_0011], [chem_001, chem_0001], 0.063361, 0.001476), Reaction([chem_001, chem_011], [chem_0011, chem_01], 25.894759, 0.048347), Reaction([chem_01, chem_01], [chem_0011], 16.858558, 14.660408), Reaction([chem_00, chem_01], [chem_0001], 6.469377, 0.169316), Reaction([chem_011, chem_0011], [chem_001, chem_0111], 31.534313, 21.501031), Reaction([chem_01, chem_011], [chem_0, chem_0111], 21.921524, 0.333969), Reaction([chem_000, chem_1], [chem_0001], 7.239927, 0.000074), Reaction([chem_111, chem_011], [chem_11, chem_0111], 23.652974, 0.087727)]

network = Network(reactions, chemicals)
dt = 0.01

def delta_reaction(reaction):
  lhs_product = reduce(lambda x, y: x*y, [chemical.conc for chemical in reaction.lhs])
  rhs_product = reduce(lambda x, y: x*y, [chemical.conc for chemical in reaction.rhs])
  
  for chemical in reaction.lhs:
    chemical.delta += rhs_product*reaction.backward - lhs_product*reaction.forward
  for chemical in reaction.rhs:
    chemical.delta += lhs_product*reaction.forward - rhs_product*reaction.backward

def simulate(network, stimulus=False, control=False):
  for chemical in network.chemicals:
    # reset delta
    chemical.delta = 0

  for reaction in network.reactions:
    # calculate generation and consumption of each chemical in each reaction
    delta_reaction(reaction)
  
  for chemical in network.chemicals:
    # calculate decay and inflow
    chemical.delta += chemical.inflow - chemical.decay*chemical.conc
    chemical.conc += chemical.delta*dt
  
  if stimulus:
    network.chemicals[0].conc = 3
  elif control:
    network.chemicals[1].conc = 3

duration = 1000
stimulus = [None] * duration
control = [None] * duration
output = [None] * duration

for i in range(duration):
  if i == 200 or i == 500 or i == 800:
    simulate(network, stimulus=True)
  elif i == 220 or i == 520 or i == 820:
    simulate(network, control=True)
  else:
    simulate(network)

  stimulus[i] = network.chemicals[0].conc
  control[i] = network.chemicals[1].conc
  output[i] = network.chemicals[2].conc

error = 0
for i in range(duration):
  if (i >= 200 and i <= 220) or (i >= 500 and i <= 520) or (i >= 800 and i <= 820):
    error += -(output[i] - 1)**2

fitness = error / 60
print(fitness)

plt.plot(stimulus, color='blue', label='Stimulus')
plt.plot(control, color='green', label='Control')
plt.plot(output, color='black', label='Output')
plt.legend()
plt.xlabel('Iteration')
plt.ylabel('Concentration')
plt.show()