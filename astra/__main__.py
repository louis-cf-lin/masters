import numpy as np, matplotlib.pyplot as plt, copy, pickle
from Env import Env
from Population import Population
from Animat import Animat

np.random.seed(0)

if __name__ == '__main__':
  GENS = 800

  env = Env()
  pop = Population()
  mean = [None] * GENS
  max = [None] * GENS
  min = [None] * GENS
  for gen in range(GENS):
    max[gen], mean[gen], min[gen] = pop.eval(env)
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
  
  print(best.genome)