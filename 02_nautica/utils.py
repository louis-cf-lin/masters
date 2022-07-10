import numpy as np

def is_near_any_objs_or_animat(animat, x, y, prox):
  if (animat.x-x)**2 + (animat.y-y)**2 < (4*prox)**2:
    return True
  for obj_type in animat.objs.keys():
    for obj in animat.objs[obj_type]:
      if (obj.x-x)**2 + (obj.y-y)**2 < prox**2:
        return True
  return False

# fitness proportionate selection to create next generation
def weighted_choice(weights):
  totals = []
  running_total = 0

  for w in weights:
    running_total += w
    totals.append(running_total)

  rnd = np.random.rand() * running_total
  for i, total in enumerate(totals):
    if rnd < total:
      return i