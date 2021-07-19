import numpy as np, matplotlib.pyplot as plt, Population, Animat, glob
from Env import EnvObject, Env

np.random.seed(100)

def prepare_to_update(env, animat):
  env.get_min_dist(animat) # finds closest object of each type
  animat.set_motor_states() # calculate outputs and set motors derivs

def update(env, animat):
  animat.update(env) # update x, y, theta

def live_life(animat, env, plot = False):
  x_traj = [None] * Animat.MAX_LIFE
  y_traj = [None] * Animat.MAX_LIFE
  fitness = 0

  for i in range(Animat.MAX_LIFE):
    x_traj[i] = animat.x
    y_traj[i] = animat.y
    prepare_to_update(env, animat)
    update(env, animat)
    fitness += sum(animat.batteries) / 400.0
    if animat.status == 'dead':
      break

  if plot:
    for i in range(Animat.MAX_LIFE)[::2]:
      circle = plt.Circle((x_traj[i], y_traj[i]), Animat.radius, fill=False, alpha=0.25)
      plt.gca().add_patch(circle)

    colors = ['g', 'b', 'r']
    for i, obj in enumerate(animat.closest_objects):
      circle = plt.Circle((obj.x, obj.y), EnvObject.radius, color=colors[i], label=obj.type, fill=False)
      plt.gca().add_patch(circle)
    plt.legend()
    plt.xlim(0, Env.MAX_X)
    plt.ylim(0, Env.MAX_Y)
    plt.show()

  animat.fitness = fitness


if __name__ == '__main__':
  # env = Env()
  # pop = Population()
  # min_fitness = [None] * glob.n_generations
  # mean_fitness = [None] * glob.n_generations
  # max_fitness = [None] * glob.n_generations

  # for i in range(glob.n_generations):
  #   pop.evaluate(env)
  #   min_fitness[i] = np.min([animat.fitness for animat in pop.animats])
  #   mean_fitness[i] = np.mean([animat.fitness for animat in pop.animats])
  #   max_fitness[i] = np.max([animat.fitness for animat in pop.animats])
  #   pop.new_gen()
  #   print(i, 'generation')

  # plt.plot(min_fitness)
  # plt.plot(mean_fitness)
  # plt.plot(max_fitness)
  # plt.show()

  # print('stop right there')

  # PSEUDO
  # ------

  # initialise environment
  # initialise population
  # for N_GENERATIONS:
  #   for each individual in population:
  #     for MAX_LIFE:
  #         calculate left wheel speed
  #         calculate right wheel speed
  #         update position
  #         if touching food
  #           replenish food battery
  #           move food object
  #         else if touching water
  #           replenish water battery
  #           move water object
  #         else if touching trap
  #           individual dies
  #           exit for loop
  #         update fitness

