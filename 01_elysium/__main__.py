import numpy as np, matplotlib.pyplot as plt, copy, pickle
from Env import Env
from Population import Population
from Animat import Animat, test_animat_trial

np.random.seed(1)

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

  GENS = 400

  env = Env()
  pop = Population()
  mean = [None] * GENS
  max = [None] * GENS
  min = [None] * GENS
  for gen in range(GENS):
    max[gen], mean[gen], min[gen] = pop.eval()
    pop.evolve()

  pop.eval(env)
  plt.plot(mean)
  plt.plot(max)
  plt.plot(min)
  plt.show()

  best = Animat()
  for animat in pop.animats:
    if animat.fitness > best.fitness:
      best = animat

  test_animat_trial(best.genome, env)

  # with open('best.pkle', 'wb') as f:
  #   pickle.dump([best], f)