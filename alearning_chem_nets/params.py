import random

random.seed(0)
max_length = 4
dt = 0.01
sigma = 0.1 # mutation rate

potential_range = [0, 7.5]
initial_conc_range = [0, 5]
inflow_range = [0, 5]
decay_range = [0, 10]
frc_range = [0, 60]

potential_sd = sigma * abs(potential_range[1] - potential_range[0])
initial_conc_sd = sigma * abs(initial_conc_range[1] - initial_conc_range[0])
inflow_sd = sigma * abs(inflow_range[1] - inflow_range[0])
decay_sd = sigma * abs(decay_range[1] - decay_range[0])
frc_sd = sigma * abs(frc_range[1] - frc_range[0])

prob_new_reaction = sigma * 5
prob_del_reaction = sigma * 5

task_duration = 1100