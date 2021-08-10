class Link(object):
  N_MID_POINTS = 2
  N_GENES = 2 + N_MID_POINTS*2 + 3

  def __init__(self):
    pass

  def set_genome(self, genome):
    NXG = Link.N_MID_POINTS