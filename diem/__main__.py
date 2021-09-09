import numpy as np, matplotlib.pyplot as plt
from Env import Env
from Population import Population
from Animat import Animat, test_animat_trial

if __name__ == '__main__':

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