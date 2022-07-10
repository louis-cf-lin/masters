import numpy as np
from animat import Animat
from obj import Obj
from controller import Controller
from sides import Sides
from pylab import *
from evolve import evolve

def test_directional_sensors():
  a = Animat()
  lx, ly = 0.5, 0.5 # obj position
  o = Obj(lx, ly, 'default')
  a.add_obj(o)

  res = np.linspace(0, 1, 50)
  mesh = np.meshgrid(res, res)

  def f(coords):
    a.x = coords[0]
    a.y = coords[1]
    a.update_sensors()
    return a.sensors['default'][Sides.LEFT]

  zs = np.apply_along_axis(f, 0, mesh)
  
  imshow(zs, extent=[0,1,0,1], origin='lower')
  
  plot(lx, ly, 'wo', label='object')
  
  xlabel('animat position')
  
  ylabel('animat position')
  
  title('Animat is facing to the right')
  
  legend()
  
  show()

def test_animat_no_controller():
  for n_animats in range(10):
    duration = 50.0
    DT = 0.02
    iterations = int(np.round(duration/DT))

    animat = Animat()
    animat.x = np.random.randn()
    animat.y = np.random.randn()
    animat.a = np.random.rand() * np.pi * 2.0
    obj = Obj(0, 0, 'default')
    animat.add_obj(obj)

    for iteration in range(iterations):
      animat.calculate_derivative()
      animat.euler_update(DT=DT)

      left_sensor = animat.sensors['default'][Sides.LEFT]
      right_sensor = animat.sensors['default'][Sides.RIGHT]

      # print(f'l:{left_sensor}\t r:{right_sensor}')

      # animat.lm = 0.4 
      # animat.rm = 0.5

      animat.lm = left_sensor * 5
      animat.rm = right_sensor * 5

    plot(animat.x_h, animat.y_h, ',')
    plot(animat.x_h[-1], animat.y_h[-1], 'ko', ms=3)

  plot(-999, -999, 'k.', label='Aniamt Final Position')
  plot(0, 0, ',', label='Animat Trajectory')
  plot(0, 0, 'rx', label='Object Position')
  xlim(-3, 3)
  ylim(-3, 3)
  legend()
  gca().set_aspect('equal')
  show()

def test_link_piecewise():
  l = Controller()
  genome = np.random.rand(Controller.N_GENES)
  l.set_genome(genome)
  xs = linspace(0, 1, 101)

  highbat_outs, lowbat_outs, unscaled_outs = [], [], []
  for x in xs :
      highbat_out, unscaled_out = l.output(x, [1.0, 1.0])
      lowbat_out, unscaled_out = l.output(x, [0.0, 0.0])
      highbat_outs.append(highbat_out)
      lowbat_outs.append(lowbat_out)
      unscaled_outs.append(unscaled_out)
  plot(xs, highbat_outs, label='high battery')
  plot(xs, lowbat_outs, label='low battery')
  plot(xs, unscaled_outs, label='no battery influence')
  xlabel('ipsilateral sensor')
  ylabel('ipsilateral motor output')
  xlim(0, 1)
  ylim(-1.05, 1.05)
  legend()
  show()


if __name__ == '__main__':
  # test_directional_sensors()

  # test_animat_no_controller()

  # test_link_piecewise()
  evolve()

