import random, pickle, params, math
from Population import Population
import matplotlib.pyplot as plt
from utils import clocked, evaluate

def main():

  task = clocked()
  errors = [None] * int(params.competitions/10)

  good_seed_found = False
  while not good_seed_found:
    error = 0
    population = Population(params.population_size)
    for network in population.networks:
      error += evaluate(network, task, 'associated')
      error += evaluate(network, task, 'unassociated')
    avg_error = error/10
    print(avg_error)
    if avg_error > -15:
      good_seed_found = True
      f = open('population_before.pckl', 'wb')
      pickle.dump(population, f)
      f.close()

  errors[0] = avg_error/10

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

    print(error)

  
  f = open('error.pckl', 'wb')
  pickle.dump(error, f)
  f.close()

  _, ax1 = plt.subplots()
  ax1.plot(errors)
  plt.show()

def analyse():

  task = clocked()

  f = open('population_before.pckl', 'rb')
  population = pickle.load(f)
  f.close()

  for k in range(1, params.competitions):

    if k == 90:
      print('this is the weird one')
      
    population.compete(clocked)

    if k % 10 == 0:
      error = 0 
      for network in population.networks:
        error += evaluate(network, task, 'associated')
        error += evaluate(network, task, 'unassociated')
      if math.isnan(error):
        print('what')
        raise Exception
    print(k)

if __name__ == '__main__':
  # main()
  analyse()


