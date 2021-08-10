import numpy as np

class Link(object):
  N_MID_POINTS = 2
  N_GENES = 2 + N_MID_POINTS*2 + 3

  def __init__(self):
    pass

  def set_genome(self, genome):
    NXG = Link.N_MID_POINTS
    NYG = Link.N_MID_POINTS + 2
    self.xs = np.array([0.0] + sorted(genome[:NXG]) + [1.0]) # enforces order
    self.ys = np.array(genome[NXG:NXG+NYG]) * 2.0 - 1.0 # scale to (-1,1)
    self.bat_sens = int(genome[NXG+NYG] < 0.5) # 0 is food, 1 is water
    self.O = genome[NXG+NYG+1] * 2.0 - 1.0 ## \in (-1,1)   
    self.S = genome[NXG+NYG+2]             ## \in (0,1)

    ## used for plotting which battery this link is sensitive to
    self.bsense = ['F','W'][self.bat_sens]

  def output(self, sens_state, bat_states):
    out = np.interp(sens_state, self.xs, self.ys)
    unscaled = out

    b = bat_states[self.bat_sens]
    b = max(min(b, 1.0), 0.0)
    out = out + b * self.O * 2.0
    out = out + out * (b * 2.0 - 1.0) * self.S

    out = max(min(out, 1.0), -1.0)

    return out, unscaled