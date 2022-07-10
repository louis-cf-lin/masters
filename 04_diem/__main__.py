import matplotlib.pyplot as plt
import pickle
from Env import Env
from Population import Population
from Animat import test_animat_trial

if __name__ == '__main__':

  TRIAL = 1
  BATCHES = 2
  BATCH_SIZE = 200

  highest_fitness = 0
  pop = Population()
  mean = [None] * BATCHES * BATCH_SIZE
  max = [None] * BATCHES * BATCH_SIZE
  min = [None] * BATCHES * BATCH_SIZE

  for batch in range(BATCHES):
    highest_fitness = 0
    fig2, axs2 = plt.subplots(figsize=(8, 8))

    for repeat in range(BATCH_SIZE):
      gen = batch * BATCH_SIZE + repeat
      print(gen)
      max[gen], mean[gen], min[gen], best = pop.eval(batch + TRIAL)
      if best.fitness > highest_fitness + 0.0001:
        highest_fitness = best.fitness
        plt.close('all')
        test_animat_trial(env=Env(batch + TRIAL), controller=best.controller.deep_copy(
        ), show=False, save=True, fname=batch)
      pop.evolve()

    with open(f'./saved_vars/trial_{TRIAL}/pop_{BATCH_SIZE}_batch_{batch}.pkl', 'wb') as f:
      pickle.dump([pop, best.controller], f)

    pop.eval(batch)
    axs2.set_title('Population trajectories')
    axs2.set_aspect('equal')
    axs2.set_xlim(Env.MIN_X, Env.MAX_X)
    axs2.set_ylim(Env.MIN_Y, Env.MAX_Y)
    for animat in pop.animats:
      axs2.plot(animat.x_hist, animat.y_hist, 'k-', ms=1, alpha=0.1)
    fig2.savefig(f'plot-population_{batch}')

  with open(f'./saved_vars/trial_{TRIAL}/pop_{BATCH_SIZE}_gen_fit.pkl', 'wb') as f:
    pickle.dump([max, mean, min], f)

  fig1, axs1 = plt.subplots(figsize=(16, 8))
  axs1.set_title('Generational fitness')
  axs1.plot(mean)
  axs1.plot(max)
  axs1.plot(min)
  axs1.set_ylabel('Fitness')
  axs1.set_xlabel('Generation')
  fig1.savefig('plot-population-fitnesses')

  print('stop')