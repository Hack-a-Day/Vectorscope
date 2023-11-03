
import math
import time

from vectorscope import Vectorscope
from random_walk import RW



def minimal_example(v):
    ## Minimal example
    for i in range(200):
        v.wave.constantX(int(math.cos(i * math.pi / 180 * 5) * 10000))
        v.wave.constantY(int(math.sin(i * math.pi / 180 * 5)* 10000))
        time.sleep_ms(10)
        
async def slot_main(v):
    minimal_example(v)
    
    