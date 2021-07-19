import numpy as np
import Animat

def Population_eval(population, env):
  for animat in population.animats:
    live_life(animat, env)

def Population_create_new_gen(population):
    new_animats = [None] * Population.SIZE
    max = np.max([animat.fitness for animat in population.animats])
    min = np.min([animat.fitness for animat in population.animats])
    i = 0
    while (None in new_animats):
      for animat in population.animats:
        p_selection = (animat.fitness - min) / (max - min + 1) # linear selection prob
        if np.random.rand() < p_selection:
          new_animats[i] = Animat(animat.genome)
          i += 1
          if i == Population.SIZE:
            population.animats = new_animats
            return

class Population:
  SIZE = 100
  def __init__(self):
    self.animats = [Animat() for _ in range(Population.SIZE)]
  
  def eval(self, env):
    Population_eval(self, env)

  def new_gen(self):
    Population_create_new_gen(self)


