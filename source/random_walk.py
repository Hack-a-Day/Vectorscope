import random
import time

class RW():
    def __init__(self, vectorscope, scale=5000, iterations=1000, delay=10):
        self.scale = scale
        self.v = vectorscope
        self.delay = delay
        self.iterations=iterations

    def random_walk(self, x, y):
        x = x + random.randint(-self.scale,self.scale) 
        y = y + random.randint(-self.scale,self.scale)
        self.v.wave.point(x,y)
        return x,y

    def go(self):
        x,y = 0,0
        for i in range(self.iterations):
            x,y = self.random_walk(x,y)
            time.sleep_ms(self.delay)



