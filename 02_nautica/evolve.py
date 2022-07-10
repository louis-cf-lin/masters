import numpy as np, os
from utils import is_near_any_objs_or_animat
from animat import Animat
from obj import Obj, ObjTypes
from controller import Controller
from multiprocessing import Pool
from plotting import plot_state_history, fitness_plots, plot_population_genepool
from utils import weighted_choice

savepath = os.path.abspath('./output/')

TEST_GA = False

DRAW_EVERY_NTH_GENERATION = 5

N_TRIALS = 5
POP_SIZE = 25
generation_index = 0
SITUATION_DURATION = 15.0
DT = 0.02
N_STEPS = int(SITUATION_DURATION / DT) # the maximum number of steps per trial

if TEST_GA:
  N_STEPS = 1
  N_TRIALS = 1

pop = [Controller() for _ in range(POP_SIZE)] # population
pop_fit_history = []


def random_obj_position(animat):
  x = np.random.rand() * 2.0 - 1.0
  y = np.random.rand() * 2.0 - 1.0
  while is_near_any_objs_or_animat(animat, x, y, 2.0 * Obj.RADIUS):
    x = np.random.rand() * 2.0 - 1.0
    y = np.random.rand() * 2.0 - 1.0
  return x, y

def simulate_trial(controller, trial_index, generating_animation=False):
  # seed for environment for this generation
  np.random.seed(generation_index*10 + trial_index)

  current_t = 0.0
  score = 0.0

  animat = Animat()
  animat.x = 0.0
  animat.y = 0.0
  animat.a = 0.0

  controller.trial_data = {}

  foods = []
  waters = []
  traps = []

  n = {
    ObjTypes.FOOD: 2,
    ObjTypes.WATER: 2,
    ObjTypes.TRAP: 2
  }
  for obj_type in ObjTypes:
    for _ in range(n[obj_type]):
      x, y = random_obj_position(animat)
      obj = Obj(x, y, obj_type)
      animat.add_obj(obj)

      if obj_type == ObjTypes.FOOD :
        foods.append(obj)
      if obj_type == ObjTypes.WATER :
        waters.append(obj)
      if obj_type == ObjTypes.TRAP :
        traps.append(obj)

  food_bat = 1.0
  water_bat = 1.0

  controller.trial_data['sample_times'] = [] 
  controller.trial_data['water_battery_h'] = []
  controller.trial_data['food_battery_h'] = []
  controller.trial_data['score_h'] = []
  controller.trial_data['eaten_FOOD_positions']  = [] 
  controller.trial_data['eaten_WATER_positions'] = []
  controller.trial_data['eaten_TRAP_positions']  = []
  controller.trial_data['FOOD_positions'] = []
  controller.trial_data['WATER_positions'] = []
  controller.trial_data['TRAP_positions'] = []

  for iteration in range(N_STEPS) :
    # battery states for plotting
    controller.trial_data['sample_times'].append(current_t)
    controller.trial_data['water_battery_h'].append(water_bat)
    controller.trial_data['food_battery_h'].append(food_bat)
    controller.trial_data['score_h'].append(score)

    if generating_animation :
      # used in animation
      controller.trial_data['FOOD_positions'].append( [(l.x,l.y) for l in foods] )
      controller.trial_data['WATER_positions'].append( [(l.x,l.y) for l in waters] )
      controller.trial_data['TRAP_positions'].append( [(l.x,l.y) for l in traps] )
    
    current_t += DT
    
    # drain battery states
    DRAIN_RATE = 0.2
    water_bat = water_bat - DT*DRAIN_RATE
    food_bat  = food_bat - DT*DRAIN_RATE

    # if going faster drains more battery
    # water_b -= (animat.lm**2) * DT * 0.01
    # food_b  -= (animat.rm**2) * DT * 0.01
    
    score += (water_bat * food_bat) * DT
    
    # pass sensor states to controller
    for obj_type in ObjTypes:
      controller.set_sensor_states(obj_type, animat.sensors[obj_type])
    # set animat motor states with controller calculations
    animat.lm, animat.rm = controller.get_motor_output((food_bat, water_bat))
    
    animat.calculate_derivative() # calculate changes
    animat.euler_update(DT=DT)    # apply changes

    # check for FOOD collisions
    for food in animat.objs[ObjTypes.FOOD] :
      if (animat.x - food.x)**2 + (animat.y - food.y)**2 < Obj.RADIUS**2 :
        food_bat += 20.0*DT
        controller.trial_data['eaten_FOOD_positions'].append( (food.x,food.y) )
        food.x, food.y = random_obj_position(animat) # relocate entity

    # check for WATER collisions
    for water in animat.objs[ObjTypes.WATER] :
      if (animat.x - water.x)**2 + (animat.y - water.y)**2 < Obj.RADIUS**2 :
        water_bat += 20.0*DT
        controller.trial_data['eaten_WATER_positions'].append( (water.x,water.y) )
        water.x, water.y = random_obj_position(animat) # relocate entity

    # check for TRAP collisions                
    for trap in animat.objs[ObjTypes.TRAP] :
      if (animat.x - trap.x)**2 + (animat.y - trap.y)**2 < Obj.RADIUS**2 :
        food_bat -= 50.0*DT
        water_bat -= 50.0*DT
        score = 0.0
        controller.trial_data['eaten_TRAP_positions'].append( (trap.x,trap.y) )
        trap.x, trap.y = random_obj_position(animat) # relocate entity

    # DEATH -- if either of the batteries reaches 0, the trial is over
    if food_bat < 0.0 or water_bat < 0.0 :
      food_bat = water_bat = 0.0
      break            

  # position of entities still not eaten at end of trial (used for plotting)
  controller.trial_data['uneaten_FOOD_positions']  = [(l.x,l.y) for l in animat.objs[ObjTypes.FOOD]]
  controller.trial_data['uneaten_WATER_positions'] = [(l.x,l.y) for l in animat.objs[ObjTypes.WATER]]
  controller.trial_data['uneaten_TRAP_positions']  = [(l.x,l.y) for l in animat.objs[ObjTypes.TRAP]]
  controller.trial_data['animat'] = animat

  if TEST_GA:
    # simple GA test -- maximise genome
    score = np.mean(controller.genome)
  
  return score

def evaluate_fitness(controller):
  trial_scores = [simulate_trial(controller, trial_index) for trial_index in range(N_TRIALS)]
  controller.fitness = np.mean(trial_scores)

  return controller

def generation():
  global pop, generation_index

  with Pool() as p:
    pop = p.map(evaluate_fitness, pop)

  # fitness of every individual controller in population
  fitnesses = [r.fitness for r in pop]
  # fitness of every individual at every generation for plotting
  pop_fit_history.append(sorted(np.array(fitnesses)))

  # plot trajectories of best and worst individual every nth gen
  if (generation_index % DRAW_EVERY_NTH_GENERATION) == 0:
    best_index = np.argmax(fitnesses)
    plot_state_history(savepath, pop[best_index], 'best')
    pop[best_index].plot_links('best')

    np.save(os.path.join(savepath,'best_genome.npy'), pop[best_index].genome)

    worst_index = np.argmin(fitnesses)
    plot_state_history(savepath, pop[worst_index], 'worst')
    pop[worst_index].plot_links('worst')

  # normalize distribution of fitnesses to lie between 0 and 1
  f_normalized = np.array([x for x in fitnesses])
  f_normalized -= min(f_normalized)
  if max(f_normalized) > 0.0 :
    f_normalized /= max(f_normalized)
  sum_f = max(0.01, sum(f_normalized))

  # probability of being selected as a parent of each individual in next generation
  ps = [f/sum_f for f in f_normalized]

  # "elitism" -- seed next generation with a copy of best individual from previous generation
  best_index = np.argmax(fitnesses)
  best_individual = pop[best_index]
  next_generation = [ Controller(genome = best_individual.genome) ]

  # populate rest of next generation by selecting parents weighted by fitness
  while len(next_generation) < POP_SIZE :
    a_i = weighted_choice(ps)
    b_i = weighted_choice(ps)
    ma = pop[a_i]
    pa = pop[b_i]
    baby = ma.procreate_with(pa)
    next_generation.append(baby)

  ## replace old generation with new
  pop = next_generation

  print(f'GENERATION # {generation_index}.\t(mean/min/max)'+
        f'({np.mean(fitnesses):.4f}/{np.min(fitnesses):.4f}/{np.max(fitnesses):.4f})')
  generation_index += 1

def evolve() :
  global fitnesses,generation_index

  print(f'Every generation is {POP_SIZE*N_TRIALS} fitness evaluations.')
  
  while True :
    fitnesses = generation()

    if generation_index % DRAW_EVERY_NTH_GENERATION == 0 :
      fitness_plots(savepath, pop_fit_history)
      plot_population_genepool(savepath, pop)