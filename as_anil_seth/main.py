import math
import numpy as np
import matplotlib.pyplot as plt

init_ofst_pos = 0
grad_1_pos = 1
thold_1_pos = 2
grad_2_pos = 3
thold_2_pos = 4
grad_3_pos = 5
S_pos = 6
O_pos = 7
bat_pos = 8

l_sgmd_pos = 9
r_sgmd_pos = 10

class Link:

  def __init__(self, genes, type):
    self.type = type
    self.set_pheno(genes)
    self.act_x = [-100, self.pheno[thold_1_pos], self.pheno[thold_2_pos], 100]
    self.calc_act_y()

  def set_pheno(self, genes):
    self.pheno = [None] * len(genes)
    for genome in [init_ofst_pos, thold_1_pos, thold_2_pos]:
      self.pheno[genome] = 200 * genes[genome] / 99 - 100 # (0,99) -> (-100,100)
    for genome in [grad_1_pos, grad_2_pos, grad_3_pos]:
      self.pheno[genome] = math.pi * genes[genome] / 99 - (math.pi / 2) # (0,99) -> (-pi/2,pi/2)
    self.pheno[S_pos] = genes[S_pos] / 99 # (0,99) -> (0,1)
    self.pheno[O_pos] = 2 * genes[O_pos] / 99 - 1 # (0,99) -> (-1,1)
    self.pheno[bat_pos] = genes[bat_pos]

  # calculate piecewise points
  def calc_act_y(self):

    def calc_grad(angle):
      return 1/math.tan(angle)
    
    init_ofst_y = self.pheno[init_ofst_pos]
    thold_1_y = init_ofst_y + calc_grad(self.pheno[grad_1_pos]) * (self.pheno[thold_1_pos] + 100)
    thold_2_y = thold_1_y + calc_grad(self.pheno[grad_2_pos]) * (self.pheno[thold_2_pos] - self.pheno[thold_1_pos])
    end = thold_2_y + calc_grad(self.pheno[grad_3_pos]) * (100 - self.pheno[thold_2_pos])

    self.act_y = [init_ofst_y, thold_1_y, thold_2_y, end]

class Animat:

  radius = 5

  def __init__(self, genes = None):
    if genes is None:
      self.init_genes()
    else:
      self.genes = genes
    self.set_pheno()
    self.init_links()
    self.links = [None] * 9
    self.l_vel = None
    self.r_vel = None
    self.water = 200 # TODO
    self.food = 200 # TODO
    self.x = 0
    self.y = 0
    self.theta = 0
    self.dx = 0
    self.dy = 0
    self.dtheta = 0
    self.fitness = 0

    for link in self.links:
      plt.plot(link.act_x, link.act_y)
  
  def init_genes(self):
    self.genes = [None] * 11
    for i in range(9):
      self.genes[i] = np.random.randint(100, size=(9)) # [0,99] inclusive
      self.genes[i][thold_2_pos] = np.random.randint(self.genes[i][thold_1_pos], 100) # enforce thold2 > thold_1
    self.genes[l_sgmd_pos] = np.random.randint(100)
    self.genes[r_sgmd_pos] = np.random.randint(100)

  def set_pheno(self):
    self.left_sgmd = 6 * self.genes[l_sgmd_pos] / 99 - 3 # (0,99) -> (-3,3)
    self.right_sgmd = 6 * self.genes[r_sgmd_pos] / 99 - 3 # (0,99) -> (-3,3)

  def init_links(self):
    for i, type in enumerate(['food', 'water', 'trap']):
      for j in range(3):
        self.links[i*3 + j] = Link(self.genes[i], type)

  def prepare_to_update(self, env):

    def euclid_dist(x1, y1, x2, y2):
      return np.sqrt((x1 - x2)**2 + (y1-y2)**2)

    def calc_dist(env, type):
      min_dist = math.inf
      if type == 'food':
        for food in env.foods:
          dist = euclid_dist(food.x, food.y, self.x, self.y)
          if dist < min_dist:
            min_dist = dist
      elif type == 'water':
        for water in env.waters:
          dist = euclid_dist(water.x, water.y, self.x, self.y)
          if dist < min_dist:
            min_dist = dist
      else:
        for trap in env.traps:
          dist = euclid_dist(trap.x, trap.y, self.x, self.y)
          if dist < min_dist:
            min_dist = dist
      return min_dist, 

    def calc_out(input, link):
      out = np.interp(input, link.act_x, link.act_y) # basic shape
      print(out)
      battery = self.water if link.pheno[bat_pos] % 2 else self.food
      out = out + ((battery / 2) * link.pheno[O_pos]) # offset modulation
      out = out + (out * (((battery - 100) / 100) * link.pheno[S_pos])) # slope modulation
      out = max(min(out, 100.0), -100.0) # \in (-100,100)
      return 2 * (out + 100) / 200 - 1 # (-100,100) -> (-1,1)
    
    def sigmoid(out, threshold):
      out = 1/(1 + np.exp(-out - threshold))
      out = 20 * out - 10 # (0,1) -> (-10,10)
      out = 5.6 * (out + 10) / 20 - 2.8 # (-10,10) -> (-2.8,2.8)
      return out
    
    l_out = 0
    r_out = 0
    for link in self.links:
      input, side = calc_dist(env, link.type)
      out = calc_out(input, link)
    
    
      self.l_vel = sigmoid(out, self.left_sgmd)
      self.r_vel = sigmoid(out, self.right_sgmd)
    else:
      self.l_vel = sigmoid(out, self.left_sgmd)
      self.r_vel = sigmoid(out*1.2, self.right_sgmd)

    print(self.l_vel)
    print(self.r_vel)


class Object:

  radius = 16

  def __init__(self, type, x = None, y = None):
    self.type = type
    if x is None:
      self.x = np.random.randint(201)  # [0,200] inclusive
    else:
      self.x = x
    if y is None:
      self.y = np.random.randint(201) # [0,200] inclusive
    else:
      self.y = y


class Population:

  pop_size = 100
  max_gens = 200 #TODO
  max_life = 800

  def __init__(self):
    self.animats = [Animat() for _ in range(self.pop_size)]
  
  def evolve(self, env):

    # def prepare_to_update(animat):
      
    #   return

    # def update(animat):

    #   return

    def calc_distance():
      return


    for animat in self.animats:
      animat.fitness = 0
      for _ in range(self.max_life):
        dist = calc_distance(animat, env)
        # prepare_to_update(animat)
        # update(animat)

  def run(self):
    for _ in range(self.max_gens):
      self.evolve()


class Env:

  num_of_foods = 1
  num_of_waters = 0 # TODO
  num_of_traps = 0 # TODO

  def __init__(self):
    self.foods = [Object('food', 100, 100) for _ in range(self.num_of_foods)]
    self.waters = [Object('water') for _ in range(self.num_of_waters)]
    self.traps = [Object('trap') for _ in range(self.num_of_traps)]


np.random.seed(814486224)

# test = Animat([[49.5, 24.75, 24.75, 74.25, 74.25, 0, 49.5, 0, 0] for _ in range(9)] + [0, 0])
# plt.ylim(-100, 100)
# plt.show()
# print(test)

pop = Population()

