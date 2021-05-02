import random, pickle, params
from Population import Population
import matplotlib.pyplot as plt
from utils import clocked, evaluate

def main():

  population = Population(params.population_size)

  task = clocked()
  errors = [None] * int(params.competitions/10)

  error = 0
  for network in population.networks:
    error += evaluate(network, task, 'associated')
    error += evaluate(network, task, 'unassociated')
  errors[0] = error/10

  i = 1
  for k in range(1 ,params.competitions):
    population.compete(clocked)

    if k % 10 == 0:
      error = 0
      for network in population.networks:
        error += evaluate(network, task, 'associated')
        error += evaluate(network, task, 'unassociated')
      errors[i] = error/10
      i += 1

    print(k)

  
  f = open('error.pckl', 'wb')
  pickle.dump(error, f)
  f.close()

  _, ax1 = plt.subplots()
  ax1.plot(errors)
  plt.show()

def analyse():

  task = clocked()

  population_before = Population(params.population_size)
  error_before = 0
  for network in population_before.networks:
    error_before += evaluate(network, task, 'associated')
    error_before += evaluate(network, task, 'unassociated')
  print(error_before/10)


  f = open('store.pckl', 'rb')
  population_after = pickle.load(f)
  f.close()

  population_after = Population(params.population_size)
  error_after = 0
  for network in population_after.networks:
    error_after += evaluate(network, task, 'associated')
    error_after += evaluate(network, task, 'unassociated')
  print(error_after/10)


if __name__ == '__main__':
  main()
  # analyse()


