from pylab import *
from sides import Sides
import numpy as np
from obj import ObjTypes
from link import Link
  
class Controller(object):

  SYMMETRIC = True

  def __init__(self, genome=None, n_sensitivities=3, n_motors=2):
    self.n_sensitivities = n_sensitivities
    self.n_motors = n_motors
    if Controller.SYMMETRIC:
      n_sides = 1
    else:
      n_sides = 2

    self.n_links = n_sensitivities * n_sides

    self.n_genes = self.n_links * Link.N_GENES

    if genome is None:
      self.genome = np.random.rand(self.n_genes)
    else:
      self.genome = genome

    self.links = np.array([
      [Link() for _ in range(n_sensitivities)]
      for _ in range(n_sides)
      ])

    self.genome_to_links()
    self.sens_states = {}

  def genome_to_links(self):
    #TODO where does links go 
    links = self.links.view().reshape(self.n_links)

    for link_i in range(self.n_links):
      link_genotype = self.genome[link_i*Link.N_GENES : (link_i+1)*Link.N_GENES]
      links[link_i].set_genome(link_genotype)

  def set_sensor_states(self, obj_type, sens_values):
    self.sens_states[obj_type] = sens_values
  
  def get_motor_output(self, bat_states):
    lm, rm = 0.0, 0.0

    for obj_type in ObjTypes:
      lm += self.links[Sides.LEFT, obj_type].output(self.sens_states[obj_type][Sides.LEFT], bat_states)[0]

      if Controller.SYMMETRIC:
        rm += self.links[Sides.LEFT, obj_type].output(self.sens_states[obj_type][Sides.RIGHT], bat_states)[0]
      else:
        rm += self.links[Sides.RIGHT, obj_type].output(self.sens_states[obj_type][Sides.RIGHT], bat_states)[0]

    return lm, rm

  def procreate_with(self, other_controller, mu=0.01, mu2=0.01):
    ma = self
    pa = other_controller

    GENOME_LEN = len(ma.genome)

    # randomly sample from ma and pa with equal probability
    baby_genome = np.where(np.random.rand(GENOME_LEN) < 0.5, ma.genome, pa.genome) 

    # mutate every gene slightly
    #TODO why mutate every gene?
    baby_genome += mu * np.random.randn(GENOME_LEN)
    
    def reflect(y):
      if y > 1.0:
        y = 1.0 - (y-1.0)
      elif y < 0.0:
        y = -y
      return y
    
    baby_genome = [reflect(x) for x in baby_genome]

    # chance of completely mutating one randomly chosen gene
    if np.random.rand() < mu2:
      gene_index = np.random.randint(GENOME_LEN)
      baby_genome[gene_index] = np.random.rand()

    return Controller(genome=baby_genome)
  
  def plot_links(self, file_prefix):
    figure()
    if Controller.SYMMETRIC:
      n_sides = 1
      sides = [Sides.LEFT]
    else:
      n_sides = 2
      sides = [Sides.LEFT, Sides.RIGHT]

    for side in sides:
      for obj_type in ObjTypes:
        l = self.links[side, obj_type]
        subplot2grid((3,n_sides),(obj_type,side))
        xs = linspace(0,1,101)
        highbat_outs = []
        lowbat_outs = []
        unscaled_outs = []
        for x in xs :
          highbat_out,unscaled_out = l.output(x,[1.0,1.0])
          lowbat_out,unscaled_out = l.output(x,[0.0,0.0])
          highbat_outs.append(highbat_out)
          lowbat_outs.append(lowbat_out)
          unscaled_outs.append(unscaled_out)
        plot(xs,highbat_outs,label='high battery')
        plot(xs,lowbat_outs,label='low battery')
        plot(xs,unscaled_outs,label='medium battery', color='black')
        text(1.02,-0.98,l.bsense[0],color='r')
        xlim(0,1)
        ylim(-1.05,1.05)
        ylabel(obj_type.name)
        if obj_type == 0:
          if not self.SYMMETRIC :
            title(side.name)
          else :
            title('Symmetric Ipsilateral Links')

    tight_layout()
    savefig(f'output/{file_prefix}_links.png',dpi=120)
    close()

