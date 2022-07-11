import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pickle

SAVE = False
VIEW = True


def import_data(batch_size, trial):
  populations = []
  champ_controllers = []

  num_of_batches = int(400 / batch_size)

  for batch in range(num_of_batches):
    with open(f'./saved_vars/trial_{trial}/pop_{BATCH_SIZE}_batch_{batch}.pkl', 'rb') as f:
      temp_pop, temp_champ_controller = pickle.load(f)
      populations.append(temp_pop)
      champ_controllers.append(temp_champ_controller)

  with open(f'./saved_vars/trial_{trial}/pop_{batch_size}_gen_fit.pkl', 'rb') as f:
    max, mean, min = pickle.load(f)

  return populations, champ_controllers, max, mean, min


def plot_gen_fit():
  sns.set_theme(style="darkgrid")
  # Load an example dataset with long-form data
  fmri = sns.load_dataset("fmri")

  # Plot the responses for different events and regions
  sns.lineplot(x="timepoint", y="signal",
               hue="region", style="event",
               data=fmri)

  if VIEW:
    plt.show()


if __name__ == '__main__':

  BATCH_SIZE = 100
  TRIAL = 0

  populations, champ_controllers, max, mean, min = import_data(
      BATCH_SIZE, TRIAL)
  plot_gen_fit()
