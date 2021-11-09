import math, numpy as np, matplotlib.pyplot as plt, copy
from collections import OrderedDict
from Sides import Sides
from Env import EnvObjectTypes, ConsumableTypes, Env
from Network import Network
from graphviz import Digraph
from globals import DT

class Animat:

  FULL_BATTERY = 1
  DRAIN_RATE = 0.5
  MAX_LIFE = 16
  RADIUS = 0.05
  SENSOR_ANGLES = [math.pi/4, -math.pi/4]

  def __init__(self, controller=None):
    if controller is None:
      self.controller = Network()
    else:
      self.controller = controller
    self.dsq = [None for _ in EnvObjectTypes]
    self.motor_hist = [[] for _ in Sides]
    self.consumption_hist = [[] for _ in ConsumableTypes]
    self.encountered = []
    self.chemical_hist = [sum(chem.conc for chem in self.controller.chemicals)]
    self.dx = None
    self.dy = None
    self.dtheta = None

    self.energy = sum(chem.conc * chem.potential for chem in self.controller.chemicals)
    self.energy_hist = [self.energy]

    # self.x = np.random.random()
    # self.y = np.random.random()
    # self.theta = np.random.random() * 2*math.pi
    self.x = Env.MAX_X
    self.x_hist = [self.x]
    self.y = Env.MIN_Y
    self.y_hist = [self.y]
    self.theta = math.pi * 5 / 8

    self.fitness = 0
    self.alive = True


  def __eq__(self, other) :
    return self.controller == other.controller and np.array_equal(self.dsq, other.dsq) and self.dx == other.dx and self.dy == other.dy and self.dtheta == other.dtheta


  def prepare(self, env):
    consumptions = np.zeros(len(EnvObjectTypes))

    for objType in EnvObjectTypes:
      for obj in env.objects[objType.value]:
        consumptions[objType.value] += ((obj.x - self.x)**2 + (obj.y - self.y)**2)**(1/2)
      self.consumption_hist[objType.value].append(consumptions[objType.value])

    left_out, right_out = self.controller.get_outputs(consumptions)
    
    # set motor state
    left_motor_state = left_out
    right_motor_state = right_out
    self.motor_hist[Sides.LEFT.value].append(left_motor_state)
    self.motor_hist[Sides.RIGHT.value].append(right_motor_state)
    # calculate derivs
    mag = (left_motor_state + right_motor_state) / 2
    self.dx = mag * math.cos(self.theta)
    self.dy = mag * math.sin(self.theta)
    self.dtheta = (right_motor_state - left_motor_state) / Animat.RADIUS


  def update(self):
    # update position and orientation
    self.x += self.dx * DT
    self.x_hist.append(self.x)
    self.y += self.dy * DT
    self.y_hist.append(self.y)
    self.theta += self.dtheta * DT

    self.energy = sum([chem.conc * chem.potential for chem in self.controller.chemicals])
    self.energy_hist.append(self.energy)
    self.chemical_hist.append(sum([chem.conc for chem in self.controller.chemicals]))

    self.fitness += self.energy * DT

    if self.energy <= 0:
      self.alive = False


  def evaluate(self, env):
    for _ in range(math.floor(Animat.MAX_LIFE / DT)):
      self.prepare(env)
      self.update()
      if not self.alive:
        break

  def graph(self):
    dot = Digraph(comment='chem', engine='neato')

    label = ['OUT LEFT', 'OUT RIGHT', 'FOOD LEFT', 'FOOD RIGHT', 'WATER LEFT', 'WATER RIGHT']

    for i, chem in enumerate(self.controller.chemicals):
      atts = { 'fontsize': '10'}
      if i < len(label):
        dot.node(chem.formula, shape='rectangle', fillcolor='gold', style='filled', label=f'<<b>{label[i]}</b><br/>{chem.formula}>', **atts)
      else:
        dot.node(chem.formula, shape='rectangle', label=f'<{chem.formula}>', **atts)
    
    for rxn in self.controller.reactions:
      atts = {'fontsize' : '10'}
      dot.node(str(rxn), shape='plaintext', label=f'<<b>{str(rxn)}</b><br/>>', **atts)
      for lhs_chem in rxn.lhs:
        dot.edge(str(rxn), lhs_chem.formula)
      for rhs_chem in rxn.rhs:
        dot.edge(str(rxn), rhs_chem.formula)

    dot.format = 'png'
    dot.render('plot-graph')


def test_animat_trial(env, controller=None, show=True, save=False, fname=''):

  if controller is None:
    animat = Animat()
  else:
    animat = Animat(controller)
  animat.evaluate(env)

  # type_colors = ['g', 'b', 'r']
  # sens_motor_subs = plt.figure(constrained_layout=True, figsize=(9,6)).subplots(2, 1)
  # sens_motor_subs[0].set_title('Left')
  # sens_motor_subs[1].set_title('Right')
  # for side in Sides:
  #   sens_motor_subs[side.value].plot(animat.motor_hist[side.value], label=f'MOTOR', color='grey')
  # for encounter in animat.encountered:
  #   for side in Sides:
  #     sens_motor_subs[side.value].axvline(x=encounter['time'], color=type_colors[encounter['type']], linestyle=':')
  #     sens_motor_subs[side.value].legend()

  # if save:
  #   plt.savefig(f'plot-sensorimotors_{fname}')

  chem_colors = ['darkorange','navajowhite','darkgreen','limegreen','darkblue','blue']
  chem_labels = ['Out L','Out R','Food','Water']
  chem = plt.figure(constrained_layout=True, figsize=(12,6)).subplots(2, 1)
  chem[0].set_title('Chemical concentrations')
  chem[1].set_title('Energy')
  for (i, chemical) in enumerate(animat.controller.chemicals):
    energy = np.array(chemical.hist) * chemical.potential
    if i < len(chem_labels):
      kwargs = { 'label': f'{chem_labels[i]} ({chemical.formula})', 'c': chem_colors[i], 'alpha': 0.75, 'zorder': 1 }
    else: 
      kwargs = { 'ls': ':', 'label': 'Other', 'c': 'black', 'alpha': 0.2, 'zorder': 0 }
    chem[0].plot(chemical.hist, **kwargs)
    chem[1].plot(energy, **kwargs)


  chem[0].set_ylabel('Chemical concs')
  total_chem_plot = chem[0].twinx()
  total_chem_plot.plot(animat.chemical_hist, c='darkviolet')
  total_chem_plot.set_ylabel('Total concs', color='darkviolet')  

  chem[1].set_ylabel('Energy')
  total_energy_plot = chem[1].twinx()
  total_energy_plot.plot(animat.energy_hist, c='darkviolet')
  total_energy_plot.set_ylabel('Total energy', color='darkviolet')

  handles, labels = chem[0].get_legend_handles_labels()
  by_label = OrderedDict(zip(labels, handles))
  chem[0].legend(by_label.values(), by_label.keys())
  chem[1].legend(by_label.values(), by_label.keys())
  

  if save:
    plt.savefig(f'plot-chems_{fname}')

  lifetime = plt.figure(constrained_layout=True, figsize=(10,5)).subplots(1,2)

  lifetime[0].set_title('Trajectory')
  lifetime[0].set_aspect('equal')
  lifetime[0].set_xlim(Env.MIN_X, Env.MAX_X)
  lifetime[0].set_ylim(Env.MIN_Y, Env.MAX_Y)
  lifetime[0].plot(animat.x_hist, animat.y_hist, 'ko', ms=1, alpha=0.5)
  lifetime[0].plot(animat.x_hist, animat.y_hist, ms=1, alpha=0.1)
  lifetime[0].add_patch(plt.Circle((animat.x_hist[0], animat.y_hist[0]), Animat.RADIUS, color='black', fill=False))
  lifetime[0].add_patch(plt.Circle((animat.x, animat.y), Animat.RADIUS, color='black'))
  env.plot(lifetime[0])

  type_colors = ['g', 'b', 'r']
  motor_subs = lifetime[1].subplots(2,1)
  motor_subs[0].set_title('Left')
  motor_subs[1].set_title('Right')
  for side in Sides:
    motor_subs[side.value].plot(animat.motor_hist[side.value], label=f'MOTOR', color='grey')
  for encounter in animat.encountered:
    for side in Sides:
      motor_subs[side.value].axvline(x=encounter['time'], color=type_colors[encounter['type']], linestyle=':')
      motor_subs[side.value].legend()
  

  if save:
    plt.savefig(f'plot-lifetime_{fname}')

  if show:
    plt.show()

  # animat.controller.print_derivs()

  print(f'Score is {animat.fitness}')

  animat.graph()

  # for reaction in animat.controller.reactions:
  #   print(reaction)

if __name__ == '__main__':

  np.set_printoptions(precision=5)

  # X = -0.25
  # Y = -0.25
  # theta = math.pi/4

  # values = np.zeros((100,100))
  # xs = np.linspace(Env.MIN_X, Env.MAX_X, 100)
  # ys = np.linspace(Env.MIN_Y, Env.MAX_Y, 100)

  # fig, ax = plt.subplots()
  # for i, x in enumerate(xs):
  #   for j, y in enumerate(ys):
  #     values[i][j] = get_sens_reading(x, y, X, Y, theta)
  # # ax.arrow(X, Y, math.cos(theta), math.sin(theta), color='red', head_width=1, head_length=1)
  # im = ax.imshow(values)
  # ax.invert_yaxis()
  # fig.colorbar(im)
  # plt.show()

  test_animat_trial(Env(0))





