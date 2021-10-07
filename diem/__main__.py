import numpy as np, matplotlib.pyplot as plt
from Env import Env
from Population import Population
from Animat import Animat, test_animat_trial

if __name__ == '__main__':

  GENS = 2000

  highest_fitness = 0
  pop = Population()
  mean = [None] * GENS
  max = [None] * GENS
  min = [None] * GENS

  env_seed = 0
  
  for gen in range(GENS):
    print(gen)
    batch = gen // 100
    if (batch != env_seed):
      env_seed = batch
      highest_fitness = 0
    max[gen], mean[gen], min[gen], best = pop.eval(env_seed)
    if best.fitness > highest_fitness + 0.1:
      highest_fitness = best.fitness
      test_animat_trial(env=Env(env_seed), controller=best.controller.deep_copy(), show=False, save=True, fname=batch)
    pop.evolve()

  pop.eval(env_seed)

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
  
  plt.savefig('population')

  print('stop')