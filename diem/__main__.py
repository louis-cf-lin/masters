import numpy as np, matplotlib.pyplot as plt
from Env import Env
from Population import Population
from Animat import Animat, test_animat_trial

if __name__ == '__main__':

  GENS = 1000

  pop = Population()
  mean = [None] * GENS
  max = [None] * GENS
  min = [None] * GENS
  for gen in range(GENS):
    print(gen)
    max[gen], mean[gen], min[gen] = pop.eval()
    pop.evolve()

  pop.eval()

  fig, axs = plt.subplots(1, 2, figsize=(16,8))
  axs[0].set_title('Generational fitness')
  axs[0].plot(mean)
  axs[0].plot(max)
  axs[0].plot(min)
  axs[0].set_ylabel('Fitness')
  axs[0].set_xlabel('Generation')
  
  axs[1].set_title('Population trajectories')
  axs[1].set_aspect('equal')
  axs[1].set_xlim(Env.MIN_X, Env.MAX_X)
  axs[1].set_ylim(Env.MIN_Y, Env.MAX_Y)
  for animat in pop.animats:
    axs[1].plot(animat.x_hist, animat.y_hist, 'k-', ms=1, alpha=0.1)
  

  best = Animat()
  for animat in pop.animats:
    if animat.fitness > best.fitness:
      best = animat

  test_animat_trial(best.controller.deep_copy())

  print('stop')