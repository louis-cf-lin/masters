from pylab import *
from enum import IntEnum
from scipy.spatial.distance import euclidean


class Animat(object) :
    def __init__(self) :
        self.reset()
        self.objs = {}
        self.sensors = {}
        self.sensors_h = {}

    def reset(self) :
        self.RADIUS = 0.1
        self.MOTOR_SPEED = 1.0
        
        ## the animat's position in a 2D space
        self.x = 0.0
        self.y = 0.0
        ## orientation (which direction it is facing). 
        ## varies between 0 and 2*pi
        self.a = 0.0

        ## lists used to track animat's position history (used
        ## primarily for plotting)
        self.x_h = []
        self.y_h = []
        self.a_h = []

        # these are the velocity of the animat's two motors.  The
        # movement of the animat is then calculated as a function of
        # these two variables.
        self.lm = 0.0 # left motor
        self.rm = 0.0 # right motor

        ## motor histories
        self.lm_h = []
        self.rm_h = []

    def add_obj(self,obj) :
        if obj.obj_type not in self.objs.keys() :
            self.objs[obj.obj_type] = []
            self.sensors[obj.obj_type] = (0.0,0.0)
            self.sensors_h[obj.obj_type] = []
        
        self.objs[obj.obj_type].append(obj)

    def update_sensors(self) :
        ## calculate sensor positions
        beta = np.pi / 4.0
        lsx = self.x + cos(self.a+beta)*self.RADIUS
        lsy = self.y + sin(self.a+beta)*self.RADIUS
        lsa = self.a + beta
        rsx = self.x + cos(self.a-beta)*self.RADIUS
        rsy = self.y + sin(self.a-beta)*self.RADIUS
        rsa = self.a - beta

        ## calculate obj impacts on sensors
        for obj_type in self.objs.keys() :
            ls = rs = 0.0
            for obj in self.objs[obj_type] :
                ls += obj.impact_sensor(lsx,lsy,lsa)
                rs += obj.impact_sensor(rsx,rsy,rsa)
            ls=min(1.0,ls)
            rs=min(1.0,rs)
            self.sensors[obj_type] = (ls,rs)
            self.sensors_h[obj_type].append((ls,rs))

    def is_close_to_any_obj_or_the_animat(self,x,y,close):
        ## calculate obj impacts on sensors
        if (self.x-x)**2 + (self.y-y)**2 < (4*close)**2 :
            return True
        
        for obj_type in self.objs.keys() :
            for obj in self.objs[obj_type] :
                if (obj.x-x)**2 + (obj.y-y)**2 < close**2 :
                    return True
        return False
            
    def calculate_derivative(self) :
        ## Given the left and right motor values of the animat, this
        ## function calculates the rate at which the x and y position
        ## of the animat and its orientation are currently changing.
        self.update_sensors()
        self.lm_h.append(self.lm)
        self.rm_h.append(self.rm)
        
        self.dx = self.MOTOR_SPEED * cos(self.a)*(self.lm+self.rm)
        self.dy = self.MOTOR_SPEED * sin(self.a)*(self.lm+self.rm)
        self.da = self.MOTOR_SPEED * (self.rm-self.lm) / self.RADIUS
        
    def euler_update(self,DT=0.02) :
        ## these lists track the position and heading of the animat
        ## for plotting purposes
        self.x_h.append(self.x)
        self.y_h.append(self.y)
        self.a_h.append(self.a)

        #### INSERT EULER INTEGRATION HERE (START)
        self.x += self.dx * DT
        self.y += self.dy * DT
        self.a += self.da * DT
        #### INSERT EULER INTEGRATION HERE (END)

        WRAP = True
        if WRAP :
            ## periodic (wrap around) boundaries
            r = 1.5 # wrap_radius 

            if self.x > r :
                self.x -= 2*r
            if self.x < -r :
                self.x += 2*r
            if self.y > r :
                self.y -= 2*r
            if self.y < -r :
                self.y += 2*r

class Obj(object) :

    RADIUS = 0.1
    def __init__(self,x,y,obj_type) :
        """
        x,y -- position
            
        obj_type -- a string or other unique identifier to allow
        different sensors to be sensitive to different 'types' of
        obj. Could be 'FOOD' or 'RED', etc.

        """
        self.x = x
        self.y = y
        self.obj_type = obj_type

    def impact_sensor(self,sensor_x,sensor_y,sensor_angle) :
        accum = 0.0
        ## compensating for wrap around obj viewing
        ## acting as if there are objs at all of these offsets
        # for lox,loy in [[-1.,0.],
        #                 [+1.,0.],
        #                 [0.,-1.],
        #                 [0.,+1.],
        #                 [0.,0.]] :
        for lox,loy in [[0.,0.]] : ## this just has one obj (no wrap around objing)
            lx = self.x + lox
            ly = self.y + loy
            
            dSq = (sensor_x - lx)**2 + (sensor_y - ly)**2

            # if the sensor were omnidirectional, its value would be
            falloff = 0.25 # lower number, sensors fall off faster
            omni = falloff/(falloff+dSq)

            # ## ... but instead, we are going to have a linear falloff
            # omni = max(0.0,1.0-dSq)
                        
            # calculate attenuation due to directionality
            # sensor to obj unit vector
            s2l = [lx - sensor_x,
                  ly - sensor_y]
            s2l_mag = np.sqrt(s2l[0]**2 + s2l[1]**2)
            if s2l_mag > 0.0 :
                s2l = [v / s2l_mag for v in s2l]

            # sensor direction unit vector
            sd = [cos(sensor_angle),
                  sin(sensor_angle)]

            # positive set of dot product
            attenuation = max(0.0,s2l[0]*sd[0] + s2l[1]*sd[1])

            accum += omni * attenuation
        return accum


def test_directional_obj_sensors() :
    r = Animat()
    lx=ly=0.5 # obj position
    l = Obj(0.5,0.5,'default')
    r.add_obj(l)

    res = linspace(0,1,50)
    xs,ys = mesh = meshgrid(res,res)

    def f(coords) :
        r.x = coords[0]
        r.y = coords[1]
        r.update_sensors()
        return r.sensors['default'][SensorSide.LEFT]

    zs = apply_along_axis(f,0,mesh)
    print(shape(zs))
    imshow(zs,extent=[0,1,0,1],origin='lower')
    plot(lx,ly,'wo',label='obj')
    xlabel('animat position')
    ylabel('animat position')
    title(f'Animat is facing to the right')
    legend()
    show()
    

if __name__ == '__main__' :
    #test_directional_obj_sensors()

    for n_animats in range(10) : 
        duration = 50.0
        DT = 0.02
        iterations = int(np.round(duration/DT))

        animat = Animat()
        animat.x = np.random.randn()
        animat.y = np.random.randn()
        animat.a = np.random.rand()*np.pi*2.0
        obj = Obj(0,0,'default')
        animat.add_obj(obj)

        for iteration in range(iterations) :
            animat.calculate_derivative()
            animat.euler_update(DT=DT)

            ## these are the current state of the animat's sensors
            left_sensor = animat.sensors['default'][SensorSide.LEFT]
            right_sensor = animat.sensors['default'][SensorSide.RIGHT]
            
            print(f'l:{left_sensor}\t r:{right_sensor}')

            ## NOT PARTICULARLY INTERESTING ROBOT
            animat.lm = 0.4 
            animat.rm = 0.5

            ## BRAITENBERG AGGRESSION
            ## animat.lm = right_sensor
            ## animat.rm = left_sensor

            ## BRAITENBERG LOVE
            # animat.lm = -left_sensor
            # animat.rm = -right_sensor

            

        plot(animat.x_h,
            animat.y_h,
            ',')

        plot(animat.x_h[-1],
            animat.y_h[-1],'ko',ms=3)

    plot(-999,-999,'k.',label=f'Animat Final Position')
    plot(0,0,',',label=f'Animat Trajectory')
    plot(0,0,'rx',label='Obj Position')
    xlim(-3,3)
    ylim(-3,3)
    legend()
    gca().set_aspect('equal')
    show()

