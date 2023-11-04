

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
# That is twp values per line (x,y) from -10000 to 10000. You should have 256 lines

# Sample file:
# -10000, -5000
# 0, -5000
# 10000, 5000

# You can use # as a comment in the file


def read_file(file_name):
    result = [[], []]
    with open(file_name, 'r') as file:
        for i, line in enumerate(file):
            line = line.strip()
            if not line.startswith('#'):
                if i == 256:
                    break
                values = line.split(',')
                if len(values) == 2:
                    result[0].append(int(values[0]))
                    result[1].append(int(values[1]))
    return result




async def kernel(v):
    ## Minimal example
    global _abort
    csv=read_file("dataxy.dat")
    csvlen=len(csv[0])
    if csvlen!=256:
        print(f"Warning wrong csv size {csvlen}")
# since read_file chops off, this shouldn't ever happen
        if csvlen>256:
            csv[0]=csv[0][:256]
            csv[1]=csv[1][:256]
# but this might            
        if csvlen<256:
            csv[0].extend([0]*(256-csvlen))
            csv[1].extend([0]*(256-csvlen))
    v.wave.packX(csv[0])
    v.wave.packY(csv[1])
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
    
    
 
