from Population import Population
from globals import TOTAL_RUNS

if __name__ == '__main__':

  TRIAL = 2
  BATCH_SIZE = 200
  BATCHES = int(TOTAL_RUNS / BATCH_SIZE)

  highest_fitness = 0
  pop = Population()
  mean = [None] * BATCHES * BATCH_SIZE
  max = [None] * BATCHES * BATCH_SIZE
  min = [None] * BATCHES * BATCH_SIZE

  for batch in range(BATCHES):
    highest_fitness = 0
    for repeat in range(BATCH_SIZE):
      gen = batch * BATCH_SIZE + repeat
      print(gen)
      max[gen], mean[gen], min[gen], best = pop.eval(batch + TRIAL)
      if best.fitness > highest_fitness:
        champ_controller = best.controller.deep_copy()
        highest_fitness = best.fitness
      pop.evolve()

    pop.eval(batch + TRIAL)
