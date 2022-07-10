import random, pickle, params, math

from numpy.core.numeric import Inf
import numpy as np
from Population import Population
import matplotlib.pyplot as plt
from utils import evaluate_population

def main():

  result = np.empty((params.population_size, params.competitions))
  population = Population()

  for i, network in enumerate(population.networks):
    result[i, 0] = network.chemicals[2].conc

  print('Error before', evaluate_population(population))

  for k in range(1, params.competitions):
    population.compete()
    for i, network in enumerate(population.networks):
      result[i, k] = network.chemicals[2].conc

  print('Error after', evaluate_population(population))


  best_fitness = -Inf
  for i, network in enumerate(population.networks):
    if network.fitness > best_fitness:
      best_fitness = network.fitness
      winner = network
      print(i)
  

  output = [None] * params.task_duration

  for chemical in winner.chemicals:
    chemical.conc = chemical.initial_conc
    output[0] = winner.chemicals[2].conc

  for i in range(1, params.task_duration):
    winner.simulate()
    output[i] = winner.chemicals[2].conc
  
  plt.plot(output)
  plt.show()


  plt.imshow(result, cmap='plasma', interpolation='nearest', aspect='auto')
  plt.colorbar()
  plt.xlabel('Generation')
  plt.ylabel('Network (individual)')

  plt.show()

if __name__ == '__main__':
  main()

