import random, pickle
from Population import Population
import matplotlib.pyplot as plt
from utils import clocked, evaluate

def main():

  population = Population(10)

  task = clocked()
  error_before = 0
  for network in population.networks:
    error_before += evaluate(network, task, 'associated')
    error_before += evaluate(network, task, 'unassociated')

  print(error_before/10)

  for _ in range(50):
    population.compete(clocked)
  
  f = open('store.pckl', 'wb')
  pickle.dump(population, f)
  f.close()

  # f = open('store.pckl', 'rb')
  # population = pickle.load(f)
  # f.close()

  print(population)

  error_after = 0
  for network in population.networks:
    error_after += evaluate(network, task, 'associated')
    error_after += evaluate(network, task, 'unassociated')

  print(error_after/10)

  # fig1, ax1 = plt.subplots()
  # ax1.plot(a_1)
  # plt.show()

  # output_b = clocked(test_b)

if __name__ == '__main__':
  main()


