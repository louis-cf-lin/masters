import random, copy
from utils import evaluate
from Network import Network

class Population:
  def __init__(self, size):
    self.networks = [None] * size
    for i in range(size):
      self.networks[i] = Network()

  def compete(self, protocol):
    random_indices = random.sample(range(len(self.networks)), 2)

    print('Competitors are index', random_indices)
    competitors = [self.networks[random_indices[0]], self.networks[random_indices[1]]]

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
      print('Winner is index', random_indices[0])
    else:
      self.networks.remove(competitors[0])
      self.networks.append(copy.deepcopy(competitors[1]))
      print('Winner is index', random_indices[1])

    self.networks[-1].mutate()