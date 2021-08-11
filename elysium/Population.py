import numpy as np, random, copy, math
import matplotlib.pyplot as plt
from Animat import Animat
from Env import Env

class Population:
  SIZE = 100
  DEME_SIZE = 10
  CROSS = 0.5
  MUT = 0.04
  def __init__(self):
    self.animats = [Animat() for _ in range(Population.SIZE)]
  
  def eval(self, env):
    fitnesses = [None] * Population.SIZE
    for i, animat in enumerate(self.animats):
      # env_instance = copy.deepcopy(env)
      env_instance = Env()
      animat.evaluate(env_instance, plot=False)

      fitnesses[i] = animat.fitness

    mean = np.mean(fitnesses)
    max = np.amax(fitnesses)
    min = np.amin(fitnesses)
    print('max:', round(max, 3), 'mean:', round(mean, 3), 'min:', round(min, 3))
    return max, mean, min

  def evolve(self):
    genomes = [copy.deepcopy(animat.genome) for animat in self.animats]
    for _ in range(10):
      a = random.randint(0, Population.SIZE-1)
      b = (a + 1 + random.randint(0, Population.DEME_SIZE-1)) % Population.SIZE # wrap around

      if (self.animats[a].fitness > self.animats[b].fitness):
        w_index = a
        l_index = b
      else:
        w_index = b
        l_index = a
      
      offspring = copy.deepcopy(self.animats[l_index].genome)
      for type_i, type_link_genome in enumerate(self.animats[w_index].genome):
        for link_i, link_genome in enumerate(type_link_genome):
          for gene_i, gene in enumerate(link_genome):
            if random.uniform(0, 1) < Population.CROSS:
              offspring[type_i][link_i][gene_i] = copy.deepcopy(gene)
            if random.uniform(0, 1) < Population.MUT:
              offspring[type_i][link_i][gene_i] = np.random.rand()

      genomes[l_index] = offspring
        
    self.animats = [Animat(genomes[animat]) for animat in range(Population.SIZE)]

