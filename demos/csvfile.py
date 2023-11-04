# simple Vectorscope "Slot"
import math
import time

from vectorscope import Vectorscope
from random_walk import RW 

import vectoros
import keyboardcb
import keyleds
import asyncio


_abort=False

# This demo reads the file /data.dat which should look like  below
# That is one value per line from -10000 to 10000. You should have 256 lines

# Sample file:
# -10000
# 0
# 10000

# You can use # as a comment in the file



def read_file(file_name):
    result = []
    recct=0
    with open(file_name, 'r') as file:
        for i, line in enumerate(file):
            if recct == 256:
                break
            line = line.strip()
            if not line.startswith('#'):
                result.append(int(line))
                recct+=1
    return result    
    




async def kernel(v):
    ## Minimal example
    global _abort
    csv=read_file("data.dat")
    csvlen=len(csv)
    if csvlen!=256:
        print(f"Warning wrong csv size {csvlen}")
# since read_file chops off, this shouldn't ever happen
        if csvlen>256:
            csv=csv[:256]
# but this might            
        if csvlen<256:
            csv.extend([0]*(256-len(csv)))
    v.wave.packX(range(-2**15,2**15,2**8))
    v.wave.packY(csv)
    while _abort==False:
       await asyncio.sleep_ms(100)   

def do_abort(key):
    global _abort
    _abort=True
    
    



async def slot_main(v):
    global _abort,_continue
    # watch the keys (D to exit)
    mykeys=keyboardcb.KeyboardCB({ keyleds.KEY_MENU: do_abort})
    await kernel(v)
    
    
 
