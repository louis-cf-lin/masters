import numpy as np, random, copy, math
import matplotlib.pyplot as plt
from Animat import Animat
from Env import Env

POP_RNG = np.random.default_rng(123456789)

class Population:
  SIZE = 100
  DEME_SIZE = 10
  CROSS = 0.5
  MUT = 0.04
  N_TOUR_ROUNDS = 5
  def __init__(self):
    self.animats = []
    # while len(self.animats) < Population.SIZE:
    #   animat = Animat()
    #   animat.evaluate(Env(), plot=False)
    #   if animat.fitness > 50:
    #     print(f'Triage {len(self.animats)}')
    #     self.animats.append(Animat(animat.controller.deep_copy()))
    self.animats = [Animat() for _ in range(Population.SIZE)]
  
  def eval(self):
    fitnesses = [None] * Population.SIZE
    for i, animat in enumerate(self.animats):
      env_instance = Env()
      animat.evaluate(env_instance, plot=False)

      fitnesses[i] = animat.fitness

    mean = np.mean(fitnesses)
    max = np.amax(fitnesses)
    min = np.amin(fitnesses)
    print('max:', round(max, 3), 'mean:', round(mean, 3), 'min:', round(min, 3))
    return max, mean, min

  def evolve(self):
    controllers = [animat.controller.deep_copy() for animat in self.animats]
    for _ in range(Population.N_TOUR_ROUNDS):
      a = POP_RNG.integers(Population.SIZE)
      b = (a + 1 + POP_RNG.integers(Population.DEME_SIZE)) % Population.SIZE # wrap around

      if (self.animats[a].fitness > self.animats[b].fitness):
        controllers[b] = controllers[a].deep_copy()
        controllers[b].mutate()
      else:
        controllers[a] = controllers[b].deep_copy()
        controllers[a].mutate()
    
    self.animats = [Animat(controller) for controller in controllers]

if __name__ == '__main__':
  pop = Population()
  pop.eval()
  pop.evolve()