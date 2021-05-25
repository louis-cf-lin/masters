from functools import reduce

def calculate_deltas(reaction):
  # calculate consumption coeff (product of LHS chemical concs)
  lhs_product = reduce(lambda x, y: x*y, [chemical.conc for chemical in reaction.lhs])
  # calculate generation coeff (product of RHS chemical concs)
  rhs_product = reduce(lambda x, y: x*y, [chemical.conc for chemical in reaction.rhs])
  
  # update chemical d/dt's
  for chemical in reaction.lhs:
    chemical.delta += rhs_product*reaction.backward - lhs_product*reaction.forward
  for chemical in reaction.rhs:
    chemical.delta += lhs_product*reaction.forward - rhs_product*reaction.backward

def simulate_step(network, stimulus_bolus=False, control_bolus=False, dt=0.01):
  # reset all deltas
  for chemical in network.chemicals:
    chemical.delta = 0

  # update deltas (generation and consumption of reactions)
  for reaction in network.reactions:
    calculate_deltas(reaction)
  
  for (i, chemical) in enumerate(network.chemicals):
    # update deltas (decay and inflow of chemicals)
    if i == 3:
      chemical.delta += chemical.inflow - chemical.decay*chemical.conc
    else:
      chemical.delta -= chemical.decay*chemical.conc

    # update concs
    chemical.conc += chemical.delta*dt
  
  # set stimulus and control chemical boluses
  if stimulus_bolus:
    network.chemicals[0].conc = 3
  elif control_bolus:
    network.chemicals[1].conc = 3