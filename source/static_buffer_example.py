import math
import time

from vectorscope import Vectorscope
from random_walk import RW



def static_buffer_example(v):
    ## Example of more complicated, repetitive waveform
    ## v.wave has two buffers of 256 samples for putting sample-wise data into: 
    ## v.wave.outBufferX and outBufferY.  These are packed 16 bits each, LSB first
    ## To make your life easier, v.wave.packX() will put a list of 16-bit ints there for you

    ramp = range(-2**15, 2**15, 2**8)
    v.wave.packX(ramp)
    sine = [int(math.sin(2*x*math.pi/256)*16_000) for x in range(256)]
    v.wave.packY(sine)
    time.sleep(5)
    ## That discontinuity and wobble is real -- 
    ##  that's what happens when you try to push around a real DAC that's bandwidth-limited.
    
async def slot_main(v):
    static_buffer_example(v)
 
