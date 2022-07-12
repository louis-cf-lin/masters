import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import pickle
from Animat import Animat
from Env import Env, EnvObject, EnvObjectTypes, ConsumableTypes
from Sides import Sides
from globals import DT, TOTAL_RUNS

SAVE = True
VIEW = False


def import_data(batch_size, num_batches, trial):
  populations = []
  champ_controllers = []

  for batch in range(num_batches):
    with open(f'./saved_vars/trial_{trial}/pop_{batch_size}_batch_{batch}.pkl', 'rb') as f:
      temp_pop, temp_champ_controller = pickle.load(f)
      populations.append(temp_pop)
      champ_controllers.append(temp_champ_controller)

  with open(f'./saved_vars/trial_{trial}/pop_{batch_size}_gen_fit.pkl', 'rb') as f:
    max, mean, min = pickle.load(f)

  return populations, champ_controllers, max, mean, min


def create_cartesian_plot(ax, animat, title, is_population=True, env=None):
  x_min, x_max, y_min, y_max = -0.5, 0.5, -0.5, 0.5

  ax.set(xlim=(x_min, x_max+0.005), ylim=(y_min-0.005, y_max),
         aspect='equal')
  ax.set_title(title, pad=10)
  ax.spines['top'].set_visible(False)
  ax.spines['right'].set_visible(False)
  ax.spines['bottom'].set_position('zero')
  ax.spines['bottom'].set_color('#9A9A9A')
  ax.spines['left'].set_position('zero')
  ax.spines['left'].set_color('#9A9A9A')

  ax.set_xlabel('$x$')
  ax.set_ylabel('$y$', rotation=0)
  ax.xaxis.set_label_coords(1, 0.57)
  ax.yaxis.set_label_coords(0.55, 0.97)

  ax.set_xticks([x_min, -0.25, 0.25, x_max])
  ax.set_yticks([y_min, -0.25, 0.25, y_max])
  ax.set_xticks([-0.25, 0.25], minor=True)
  ax.set_yticks([-0.25, 0.25], minor=True)
  ax.tick_params(axis='both', colors='#9A9A9A')
  ax.grid(which='both', color='#E0E0E0',
          linewidth=1, linestyle='-', alpha=0.2)

  if is_population:
    ax.plot(animat.x_hist, animat.y_hist, 'b-', linewidth=0.25, alpha=0.2)
  else:
    ax.plot(animat.x_hist, animat.y_hist, 'ko', ms=1, alpha=0.5)
    ax.plot(animat.x_hist, animat.y_hist, ms=1, alpha=0.1)
    ax.add_patch(plt.Circle(
        (animat.x_hist[0], animat.y_hist[0]), Animat.RADIUS, color='black', fill=False))
    ax.add_patch(plt.Circle((animat.x, animat.y),
                 Animat.RADIUS, color='black'))
    colors = ['#29C943', '#0D40FB']
    for type in EnvObjectTypes:
      for object in env.objects[type.value]:
        ax.add_patch(plt.Circle((object.x, object.y),
                     EnvObject.RADIUS, color=colors[type.value]))
    for object in env.consumed:
      ax.add_patch(plt.Circle((object.x, object.y), EnvObject.RADIUS,
                   color=colors[EnvObjectTypes[object.type].value], fill=False))


def plot_population_fitnesses(batch_size, max, mean, min):
  sns.set_theme(context='paper',
                font_scale=1, rc={'lines.linewidth': 1, 'axes.facecolor': '#EAEAF3'})

  max_df = pd.DataFrame(
      {'gen': range(TOTAL_RUNS), 'fitness': max, 'param': 'champ'})
  mean_df = pd.DataFrame(
      {'gen': range(TOTAL_RUNS), 'fitness': mean, 'param': 'average'})
  min_df = pd.DataFrame(
      {'gen': range(TOTAL_RUNS), 'fitness': min, 'param': 'worst'})

  df = pd.concat([max_df, mean_df, min_df], ignore_index=True)

  ax = sns.lineplot(x='gen', y='fitness', data=df,
                    hue='param', palette='bright')
  ax.fill_between(range(TOTAL_RUNS), max, alpha=0.1, color='#0D40FB')
  ax.fill_between(range(TOTAL_RUNS), mean, alpha=0.1, color='#FD7A22')
  ax.fill_between(range(TOTAL_RUNS), min, alpha=0.1, color='#29C943')
  ax.set(title=f'Batch size = {batch_size}', xlim=(
      0, TOTAL_RUNS), ylim=(0, 200), xlabel='Generation', ylabel='Fitness')
  ax.legend_.set_title(None)

  if SAVE:
    ax.get_figure().savefig(f'./figs/bs_{batch_size}_gen_fit', dpi=800)


def plot_population_trajectories(batch_size, populations):
  matplotlib.rc_file_defaults()

  def create_plot(ax, population, i):
    for animat in population.animats:
      create_cartesian_plot(ax, animat, f'Batch {i+1}')

  if (batch_size == 50):
    fig, ax = plt.subplots(3, 3, figsize=(15, 15))
    for i, population in enumerate(populations):
      create_plot(ax[int(i / 3), i % 3], population, i)
    fig.subplots_adjust(wspace=0.1, hspace=0.25)
    fig.delaxes(ax[2, 2])
  elif (batch_size == 100):
    fig, ax = plt.subplots(2, 2, figsize=(10, 10))
    for i, population in enumerate(populations):
      create_plot(ax[int(i / 2), i % 2], population, i)
    fig.subplots_adjust(wspace=0.15, hspace=0.25)
  else:
    fig, ax = plt.subplots(1, 2, figsize=(10, 5))
    for i, population in enumerate(populations):
      create_plot(ax[i], population, i)
    fig.subplots_adjust(wspace=0.2, hspace=0.25)

  fig.patch.set_facecolor('#ffffff')

  if SAVE:
    fig.savefig(f'./figs/bs_{batch_size}_trajectories',
                dpi=800, bbox_inches='tight')


def plot_life(batch_size, animats, envs):
  matplotlib.rc_file_defaults()
  if (batch_size == 50):
    fig, axs = plt.subplots(2, 4, figsize=(20, 10))
  elif (batch_size == 100):
    fig, axs = plt.subplots(1, 4, figsize=(20, 5))
  else:
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))

  for i, ax in enumerate(axs.flatten()):
    create_cartesian_plot(
        ax, animats[i], f'Batch {i+1}', is_population=False, env=envs[i])

  if SAVE:
    fig.savefig(f'./figs/bs_{batch_size}_life',
                dpi=1200, bbox_inches='tight')


def plot_battery(batch_size, animats):
  matplotlib.rc_file_defaults()
  sns.set_theme(style='whitegrid', rc={"grid.color": "#F2F2F2"})
  dfs = []
  for batch, animat in enumerate(animats):
    for type in ConsumableTypes:
      dict = {'timestep': range(len(
          animat.battery_hist[type.value])), 'level': animat.battery_hist[type.value], 'type': type.name.capitalize(), 'batch': f'Batch {batch+1}'}
      dfs.append(pd.DataFrame(dict))

  data = pd.concat(dfs, ignore_index=True)
  g = sns.relplot(x='timestep', y='level', hue='type', style='type', col='batch', col_wrap=2, height=1.5,
                  aspect=4, linewidth=1, kind='line', palette=['#29C943', '#0D40FB'], alpha=0.75, data=data)
  g.set(xlim=(0, int(Animat.MAX_LIFE/DT)), ylim=(0, 1))
  g.set_titles('{col_name}')

  g._legend.remove()
  handles, labels = g.axes[0].get_legend_handles_labels()
  g.fig.legend(handles, labels, title=None, ncol=2,
               bbox_to_anchor=(0.92, -0.02), loc='lower right')

  g.set_axis_labels('', '')  # remove subplot labels
  g.fig.text(x=0, y=0.5, verticalalignment='center',
             s='Battery level', size=14, rotation=90)
  g.fig.text(x=0.5, y=0, horizontalalignment='center',
             s='Time step',  size=14)

  if SAVE:
    g.fig.savefig(f'./figs/bs_{batch_size}_battery',
                  dpi=800, bbox_inches='tight')


def plot_sensorimotors(batch_size, animats):
  matplotlib.rc_file_defaults()
  sns.set_theme(style='whitegrid', rc={"grid.color": "#F2F2F2"})

  dfs = []
  for batch, animat in enumerate(animats):
    for side in Sides:
      for type in ConsumableTypes:
        dict = {'timestep': range(len(animat.sens_hist[side.value][type.value])), 'value': animat.sens_hist[side.value]
                [type.value], 'side': side.name.capitalize(), 'type': type.name.capitalize(), 'component': 'Sensor', 'batch': f'Batch {batch+1}'}
        dfs.append(pd.DataFrame(dict))
      dict = {'timestep': range(len(animat.motor_hist[side.value])), 'value': animat.motor_hist[side.value], 'side': side.name.capitalize(
      ), 'type': 'Motor speed', 'component': 'Motor', 'batch': f'Batch {batch+1}'}
      dfs.append(pd.DataFrame(dict))

  data = pd.concat(dfs, ignore_index=True)
  g = sns.relplot(x='timestep', y='value', hue='type', style='component', row='batch', col='side',
                  height=2, aspect=2, linewidth=1, kind='line', palette=['#29C943', '#0D40FB', '#FEC32D'], alpha=0.75, data=data)

  g.set(xlim=(0, int(Animat.MAX_LIFE/DT)))
  g.set_titles('{row_name} | {col_name}')

  g._legend.remove()
  g.fig.legend(['Food sensor', 'Water sensor', 'Motor speed'],
               bbox_to_anchor=(0.85, 1.03), loc='upper right', ncol=3)

  g.set_axis_labels('', '')  # remove subplot labels
  g.fig.text(x=0, y=0.5, verticalalignment='center',
             s='Sensor value', size=14, rotation=90)
  g.fig.text(x=0.5, y=0, horizontalalignment='center',
             s='Time step',  size=14)

  if SAVE:
    g.fig.savefig(f'./figs/bs_{batch_size}_sm',
                  dpi=800, bbox_inches='tight')


def plot_chemicals(batch_size, animats, plot_energy=False):
  matplotlib.rc_file_defaults()
  sns.set_theme(style='whitegrid', rc={"grid.color": "#F2F2F2"})

  labels = ['Out Left', 'Out Right', 'Food Left',
            'Food Right', 'Water Left', 'Water Right']
  dfs = []
  for batch, animat in enumerate(animats):
    for i, chem in enumerate(animat.controller.chemicals):
      dict = {
          'timestep': range(len(chem.hist)),
          'value': np.array(chem.hist) * chem.potential if plot_energy else chem.hist,
          'id': i,
          'type': labels[i].split(' ')[0] if i < len(labels) else 'Other',
          'side': labels[i].split(' ')[1] if i < len(labels) else 'Other',
          'batch': f'Batch {batch+1}',
      }
      dfs.append(pd.DataFrame(dict))

  data = pd.concat(dfs, ignore_index=True)
  g = sns.relplot(x='timestep', y='value', hue='type', style='side', row='batch', units='id',
                  height=2, aspect=2, linewidth=1, kind='line', estimator=None, ci=None,
                  palette=['#FD7A22', '#29C943', '#0D40FB', '#DADADA'], alpha=0.5, data=data)

  g.set(xlim=(0, int(Animat.MAX_LIFE/DT)), ylim=(0, None))
  g.set_titles('{row_name}')

  g._legend.remove()
  if plot_energy:
    g.fig.legend(['Out | Left', 'Out | Right', 'Food | Left', 'Food | Right', 'Water | Left', 'Water | Right',
                  'Other'], bbox_to_anchor=[1.11, 0.5], loc='center right', frameon=False, labelspacing=2)

  g.set_axis_labels('', '')  # remove subplot labels
  g.fig.text(x=0.05, y=0.5, verticalalignment='center',
             s='Energy (concentration x standard potential)' if plot_energy else 'Chemical concentration',
             size=14, rotation=90)
  g.fig.text(x=0.5, y=0.005, horizontalalignment='center',
             s='Time step',  size=14)

  if SAVE:
    g.fig.savefig(f'./figs/bs_{batch_size}_{"energy" if plot_energy else "chems"}',
                  dpi=800, bbox_inches='tight')


if __name__ == '__main__':

  TRIAL = 0
  BATCH_SIZE = 200

  num_batches = int(TOTAL_RUNS / BATCH_SIZE)

  populations, champ_controllers, max, mean, min = import_data(
      BATCH_SIZE, num_batches, TRIAL)

  # plot_population_fitnesses(BATCH_SIZE, max, mean, min)

  # plot_population_trajectories(BATCH_SIZE, populations)

  champ_animats = []
  envs = []
  for batch, controller in enumerate(champ_controllers):
    env = Env(batch + TRIAL)
    animat = Animat(controller)
    animat.evaluate(env)
    champ_animats.append(animat)
    envs.append(env)

  # plot_life(BATCH_SIZE, champ_animats, envs)

  plot_battery(BATCH_SIZE, champ_animats)

  # plot_sensorimotors(BATCH_SIZE, champ_animats)

  # plot_chemicals(BATCH_SIZE, champ_animats)
  # plot_chemicals(BATCH_SIZE, champ_animats, plot_energy=True)

  if VIEW:
    plt.show(block=True)
