import numpy as np, matplotlib.pyplot as plt, copy
from Env import Env
from Population import Population
from Animat import Animat

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
  for gen in range(2):
    results[gen] = pop.eval(env)
    pop.evolve()

  plt.plot(results)
  plt.show()

  best = Animat()
  for animat in pop.animats:
    if animat.fitness > best.fitness:
      best = animat
  
  plt.figure(figsize=(8,8))
  # plt.xlim(0, Env.MAX_X)
  # plt.ylim(0, Env.MAX_Y)
  x = [None] * Animat.MAX_LIFE
  y = [None] * Animat.MAX_LIFE
  theta = [None] * Animat.MAX_LIFE
  left_food = [None] * Animat.MAX_LIFE
  left_water = [None] * Animat.MAX_LIFE
  left_trap = [None] * Animat.MAX_LIFE
  right_food = [None] * Animat.MAX_LIFE
  right_water = [None] * Animat.MAX_LIFE
  right_trap = [None] * Animat.MAX_LIFE
  best.plot(False, 'red', 1, True)
  for i in range(Animat.MAX_LIFE):
    left_food[i], left_water[i], left_trap[i], right_food[i], right_water[i], right_trap[i] = best.prepare(env)
    best.update()
    best.plot(False)
    if not best.alive:
      break
  best.plot(False, 'green', 1, True)
  env.plot(False)

  fig, axs = plt.subplots(2)
  axs[0].set_title('Left')
  axs[0].plot(left_food, color='g')
  axs[0].plot(left_water, color='b')
  axs[0].plot(left_trap, color='r')
  axs[1].set_title('Right')
  axs[1].plot(right_food, color='g')
  axs[1].plot(right_water, color='b')
  axs[1].plot(right_trap, color='r')
  plt.show()
