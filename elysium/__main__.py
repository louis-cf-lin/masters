import numpy as np, matplotlib.pyplot as plt, copy
from Env import Env
from Population import Population
from Animat import Animat, test_animat_trial

np.random.seed(0)

if __name__ == '__main__':
  # PSEUDO
  # ------

  # initialise environment
  # initialise population
  # for N_GENERATIONS:
  #   reset environment
  #   for each individual in population:
  #   |  for MAX_LIFE:
  #   |  |
  #   |  |  prepare:
  #   |  |  |  store closest object of each type
  #   |  |  |  for each side:
  #   |  |  |  |  for each closest object:
  #   |  |  |  |  |  calculate distance from sensor to object
  #   |  |  |  |  |  transform distance to input
  #   |  |  |  |
  #   |  |  |  |  calculate motor state on that side
  #   |  |  |
  #   |  |  |  calculate dx, dy, dtheta
  #   |  |
  #   |  |  update:
  #   |  |  |  update x, y, theta
  #   |  |  |  if touching food:
  #   |  |  |  |  replenish food battery
  #   |  |  |  |  move food object
  #   |  |  |  else if touching water:
  #   |  |  |  |  replenish water battery
  #   |  |  |  |  move water object
  #   |  |  |  else if touching trap:
  #   |  |  |  |  individual dies
  #   |  |  |  
  #   |  |  |  if both batteries 0:
  #   |  |  |  |  individual dies
  #   |  |  |
  #   |  |  |  update fitness
  #   |  |   
  #   |  |  if individual is dead:
  #   |  |  |  next   
  #   |     

  GENS = 100
  env = Env()
  pop = Population()
  results = [None] * GENS
  for gen in range(20):
    results[gen] = pop.eval(env)
    pop.evolve()

  pop.eval(env)
  plt.plot(results)
  plt.show()

  best = Animat()
  for animat in pop.animats:
    if animat.fitness > best.fitness:
      best = animat

  test_animat_trial(best.genome, env)
