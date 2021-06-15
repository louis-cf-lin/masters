import math
import matplotlib.pyplot as plt

class Animat:

  diam = 10
  
  def __init__(self):
    self.x = 0
    self.y = 0
    self.dx = 0
    self.dy = 0
    self.theta = 0
    self.dtheta = 0
    self.v_l = 2.8
    self.v_r = 0
  
  def prepare_to_update(self):
    magnitude = (self.v_l + self.v_r) / 2
    self.dx = magnitude * math.cos(self.theta)
    self.dy = magnitude * math.sin(self.theta)
    self.dtheta = (self.v_l - self.v_r) / Animat.diam

  def update(self):
    self.x += self.dx
    self.y += self.dy
    self.theta += self.dtheta
    return self.x, self.y


duration = 1000
dude = Animat()

out_x = [None] * duration
out_y = [None] * duration

for i in range(duration):
  dude.prepare_to_update()
  out_x[i], out_y[i] = dude.update()

plt.plot(out_x, out_y)
plt.show()