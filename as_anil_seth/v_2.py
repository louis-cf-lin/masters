import math
import numpy as np
import matplotlib as plt

START_Y = 0
CTRL1_X = 1
CTRL1_Y = 2
CTRL2_X = 3
CTRL2_Y = 4
END_Y = 5
O = 6
S = 7
BAT = 8

L_SGMD = 9
R_SGMD = 10

class Link:
  N_GENES = 9
  def __init__(self, genome):
    self.set_genome(genome)

  def set_genome(self, genome):
    self.ctrl_x = [0] + [genome[CTRL1_X], genome[CTRL2_X]] + [1] # (0,1)
    self.ctrl_y = np.array([genome[START_Y], genome[CTRL1_Y], genome[CTRL2_Y], genome[END_Y]]) * 2.0 - 1.0 # (-1,1)
    self.O = genome[O] # (-1,1)
    self.S = genome[S] # (0,1)
    self.infl_bat = genome[BAT]

  def output(self, input, battery):
    out = np.interp(input, self.ctrl_x, self.ctrl_y)
    unscaled = out

    B = battery[self.infl_bat]
    out = out + B * self.O # offset (-1,1)
    out = out + out * (B * 2.0 - 1.0) * self.S # multiply (-1,1), i.e. double or cancel

    out = max(min(out, 1.0), -1.0)
    
    return out, unscaled

class Animat:
  n_sensors = 3
  n_links_to_sensors = 3
  n_sides = 1 # symmetric
  n_links = n_sensors * n_links_to_sensors * n_sides
  N_GENES = n_links * Link.N_GENES

  def __init__(self, genome=None):
    if genome is None:
      self.genome = np.random.rand(Animat.N_GENES)
    else:
      self.genome = genome
    self.links = [[Link() for _ in range(Animat.n_links_to_sensors)] for side in range(Animat.n_sides)]
    print(self.links)

dude = Animat()