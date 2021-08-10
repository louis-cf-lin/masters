from pylab import *
import os
from controller import Controller
from obj import ObjTypes, Obj
from mpl_toolkits.axes_grid1 import make_axes_locatable

DPI = 90

def plot_state_history(savepath, controller, file_prefix) :
  animat = controller.trial_data['animat']
  
  figure()
  plot(animat.x_h, animat.y_h, 'k,', lw=0.5, alpha=0.5, label='Animat Trajectory')
  plot(animat.x_h[-1], animat.y_h[-1], 'k.', label='Animat Final Position',markersize=15.0)
  c = plt.Circle((animat.x_h[-1],animat.y_h[-1]), animat.RADIUS, color='k',fill=True)
  gca().add_patch(c)
  for obj_type in ObjTypes:
    colors = {
      ObjTypes.FOOD: 'g',
      ObjTypes.WATER: 'b',
      ObjTypes.TRAP: 'r',
    }
    for x, y in controller.trial_data[f'eaten_{obj_type.name}_positions'] :
      c = plt.Circle((x,y), Obj.RADIUS, color=colors[obj_type], fill=False)
      gca().add_patch(c)
    for x,y in controller.trial_data[f'uneaten_{obj_type.name}_positions'] :
      c = plt.Circle((x,y), Obj.RADIUS, color=colors[obj_type])
      gca().add_patch(c)
  xlim(-1.5, 1.5)
  ylim(-1.5, 1.5)
  gca().set_aspect('equal')
  savefig(os.path.join(savepath,f'{file_prefix}_spatial.png'), dpi=DPI)
  close()

  dur = max(controller.trial_data['sample_times'])
  
  figure()
  subplot2grid((4,1), (0,0))
  plot(controller.trial_data['sample_times'], controller.trial_data['water_battery_h'], 'b-', label='water')
  plot(controller.trial_data['sample_times'], controller.trial_data['food_battery_h'], 'g-', label='food')
  ylabel('batteries')
  ylim(0.0, 3.5)
  xlim(0, dur)
  xticks([])
  legend()

  subplot2grid((4,1), (1,0))
  plot(controller.trial_data['sample_times'], controller.trial_data['score_h'], 'k-', label='score')
  ylabel('score')
  # ylim(0.0,3.5)
  xlim(0, dur)
  xticks([])
  legend()
  
  subplot2grid((4,1), (2,0))
  for obj_type in ObjTypes:
    colors = {
      ObjTypes.FOOD: '#00ff00',
      ObjTypes.WATER: '#0000ff',
      ObjTypes.TRAP: '#ff0000',
    }
    s_h = np.array(animat.sensors_h[obj_type])
    
    plot(controller.trial_data['sample_times'], s_h[:,0], color=colors[obj_type], ls='-')
    plot(controller.trial_data['sample_times'], s_h[:,1], color=colors[obj_type], ls='--')
  xticks([])
  ylim(0, 1)
  xlim(0, dur)
  ylabel('sensors')

  subplot2grid((4,1), (3,0))
  plot(controller.trial_data['sample_times'], animat.lm_h, color='k', ls='-', label='left')
  plot(controller.trial_data['sample_times'], animat.rm_h, color='k', ls='--', label='right')
  ylim(-3, 3)
  xlim(0, dur)
  ylabel('motors')
  savefig(os.path.join(savepath,f'{file_prefix}_timeseries.png'), dpi=DPI)
  tight_layout()
  close()

def fitness_plots(savepath,pop_fit_history) :
  figure() ## detailed fitness plot
  n_generations = np.shape(pop_fit_history)[0]
  pop_size = np.shape(pop_fit_history)[1]
  im = imshow(np.array(pop_fit_history).T, aspect='auto', extent=[0,n_generations,0,pop_size])
  xticks(range(n_generations))    
  xlabel('generation')
  ylabel('individual (sorted by fitness)')
  title('fitness')
  ## draw colorbar
  divider = make_axes_locatable(gca())
  cax = divider.append_axes("right", size="5%", pad=0.05)
  plt.colorbar(im, cax=cax)
  tight_layout()
  savefig(os.path.join(savepath,'fitness_history.png'),dpi=DPI)
  close()

  figure() ## summary of fitness plot (mean and max)
  means = np.mean(np.array(pop_fit_history), axis=1)
  stddevs = np.std(np.array(pop_fit_history), axis=1)
  maxes = np.max(np.array(pop_fit_history), axis=1)
  #plot(means,'k',label='mean fitness')
  errorbar(range(n_generations), means, stddevs, label='mean and std fitness ')
  plot(maxes, 'r', label='max fitness')#,alpha=0.5,lw=0.5)
  if n_generations > 1:
    xlim(0, n_generations-1)
  legend()
  xlabel('generation')
  ylabel('fitness')
  tight_layout()
  savefig(os.path.join(savepath,'fitness_history_summary.png'), dpi=DPI)
  close()


def plot_population_genepool(savepath, pop) :
  figure()
  pop_size = len(pop)
  g = np.zeros((pop[0].n_genes,pop_size))
  for index in range(pop_size):
    g[:,index] = pop[index].genome
  imshow(g)
  xlabel('individual')
  ylabel('gene')
  colorbar()
  tight_layout()
  savefig(os.path.join(savepath,'population_genepool.png'),dpi=DPI)
  close()
