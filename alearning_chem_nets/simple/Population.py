import random, copy, params
from utils import mutate_network
from Network import Network

class Population:
  def __init__(self):
    self.networks = [None] * params.population_size
    for i in range(params.population_size):
      self.networks[i] = Network()

  def compete(self):
    random_indices = random.sample(range(len(self.networks)), 2)

    competitors = [self.networks[random_indices[0]], self.networks[random_indices[1]]]

    if competitors[0].fitness > competitors[1].fitness:
      self.networks[random_indices[1]] = mutate_network(copy.deepcopy(competitors[0]))
      # print('Individual', random_indices[0], 'replacing', random_indices[1])
    else:
      self.networks[random_indices[0]] = mutate_network(copy.deepcopy(competitors[1]))
      # print('Individual', random_indices[1], 'replacing', random_indices[0])
    