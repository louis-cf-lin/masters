import random

def concatenate(*args):
  return ''.join(*args)

def rand_split(chemical, max_length=4):
  length = len(chemical)
  if length > max_length:
    pos = random.randint(length - max_length, max_length)
  else:
    pos = random.randrange(1, length)
  return [chemical[:pos], chemical[pos:]]

def polymer(type, *args):
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

def compete(network_1, network_2):
  if network_1.fitness > network_2.fitness:
    return network_1, network_2
  else:
    return network_2, network_1

