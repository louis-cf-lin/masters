import numpy as np
from Animat import Animat
from Env import Env

POP_RNG = np.random.default_rng(123456789)


class Population:
  SIZE = 100
  DEME_SIZE = 10
  MUT = 0.04
  N_TOUR_ROUNDS = 10

  def __init__(self):
    self.animats = [Animat() for _ in range(Population.SIZE)]

  def eval(self, generation):
    fitnesses = [None] * Population.SIZE
    for i, animat in enumerate(self.animats):
      env = Env(generation)
      animat.evaluate(env)

      fitnesses[i] = animat.fitness

    best_index = np.argmax(fitnesses)
    max = fitnesses[best_index]
    mean = np.mean(fitnesses)
    min = np.amin(fitnesses)
    print('max:', round(max, 3), 'mean:',
          round(mean, 3), 'min:', round(min, 3))
    return max, mean, min, self.animats[best_index]

  def evolve(self):
    controllers = [animat.controller.deep_copy() for animat in self.animats]
    for _ in range(Population.N_TOUR_ROUNDS):
      a = POP_RNG.integers(Population.SIZE)
      b = (a + 1 + POP_RNG.integers(Population.DEME_SIZE)
           ) % Population.SIZE  # wrap around

      if (self.animats[a].fitness > self.animats[b].fitness):
        controllers[b] = controllers[a].deep_copy()
        controllers[b].mutate()
      else:
        controllers[a] = controllers[b].deep_copy()
        controllers[a].mutate()

    self.animats = [Animat(controller) for controller in controllers]
