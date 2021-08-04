import numpy as np, math

class Obj(object):

  RADIUS = 0.1
  
  def __init__(self, x, y, obj_type):
    self.x = x
    self.y = y
    self.obj_type = obj_type

  def impact_sensor(self, sens_x, sens_y, sens_a):
    d_sq = (sens_x - self.x)**2 + (sens_y - self.y)**2

    falloff = 0.25
    omni = falloff / (falloff + d_sq)

    s2l = [self.x - sens_x,
          self.y - sens_y]
    s2l_mag = np.sqrt(d_sq)
    if s2l_mag > 0.0:
      s2l = [v / s2l_mag for v in s2l]
    
    sd = [math.cos(sens_a),
          math.sin(sens_a)]
    
    attenuation = max(0.0, s2l[0]*sd[0] + s2l[1]+sd[1])

    return omni * attenuation

class Animat(object):

  RADIUS = 0.1
  MOTOR_SPEED = 1.0
  
  def __init__(self):
    self.reset()
    self.objs = {}
    self.sensors = {}
    self.sensors_h = {}

  def reset(self):
    self.x = 0.0
    self.y = 0.0
    self.a = 0.0

    self.x_h = []
    self.y_h = []
    self.a_h = []

    self.lm = 0.0
    self.rm = 0.0

    self.lm_h = []
    self.rm_h = []

  def add_obj(self, obj):
    if obj.obj_type not in self.objs.keys():
      self.objs[obj.obj_type] = []
      self.sensors[obj.obj_type] = (0.0, 0.0)
      self.sensors_h[obj.obj_type] = []
    
    self.objs[obj.obj_type].append(obj)

  def update_sensors(self):
    beta = np.pi / 4.0 # angle between front and sensors
    
    lsa = self.a + beta
    lsx = self.x + math.cos(lsa)*Animat.RADIUS
    lsy = self.y + math.sin(lsa)*Animat.RADIUS

    rsa = self.a - beta
    rsx = self.x + math.cos(rsa)*Animat.RADIUS
    rsy = self.x + math.cos(rsa)*Animat.RADIUS

    for obj_type in self.objs.keys():
      ls, rs = 0.0, 0.0
      for obj in self.objs[obj_type]:
        ls += obj.impact_sensor(lsx, lsy, lsa)
        rs += obj.impact_sensor(rsx, rsy, rsa)
      ls = min(1.0, ls)
      rs = min(1.0, rs)
      self.sensors[obj_type] = (ls, rs)
      self.sensors_h[obj_type].append((ls, rs))

  def calculate_derivative(self):
    self.update_sensors()
    self.lm_h.append(self.lm)
    self.rm_h.append(self.rm)

    self.dx = Animat.MOTOR_SPEED * math.cos(self.a) * (self.lm + self.rm)
    self.dy = Animat.MOTOR_SPEED * math.sin(self.a) * (self.lm + self.rm)
    self.da = Animat.MOTOR_SPEED * (self.rm - self.lm) / Animat.RADIUS
  
  def euler_update(self, DT=0.02):
    self.x_h.append(self.x)
    self.y_h.append(self.y)
    self.a_h.append(self.a)

    self.x += self.dx * DT
    self.y += self.dy * DT
    self.a += self.da * DT

    r = 1.5
    if self.x > r:
      self.x -= 2*r
    elif self.x < -r:
      self.x += 2*r
    if self.y > r:
      self.y -= 2*r
    elif self.y < -r:
      self.y += 2*r

