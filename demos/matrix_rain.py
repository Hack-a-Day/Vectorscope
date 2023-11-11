from vectorscope import Vectorscope
import random 
import time

try:
    v = Vectorscope()
except:
    ## prevents OS 16 -- out of DMA error
    ## but at the cost of resetting half the damn time
    print("No free DMAs.  Resetting... try again in a sec.")
    machine.reset()

top = const(-2**15)
steps = const(1024)

while True:
    ## Pick a new horizontal start
    x = random.randint(-28000,28000)
    v.wave.constantX(x)
    ## Drip drip drip
    for y in range(top, random.randint(0,32000), steps):
        ## Wait for buffer to get empty
        while not v.wave.outBuffer_ready:  
            pass
        v.wave.packY(range(y, y+steps, steps//256))
        v.wave.outBuffer_ready = False


