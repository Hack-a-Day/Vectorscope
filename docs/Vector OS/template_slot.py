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

async def kernel(v):
    ## Minimal example
    global _abort
    while _abort==False:
        for t in range(200):
            if _abort:
                break
            v.wave.constantX(int(math.cos(t * math.pi / 180 * 5) * 10000))
            v.wave.constantY(int(math.sin(t * math.pi / 180 * 5)* 10000))
            await asyncio.sleep_ms(10)
            

def do_abort(key):
    global _abort
    _abort=True
    
    



async def slot_main(v):
    global _abort,_continue
    # watch the keys (MENU to exit)
    mykeys=keyboardcb.KeyboardCB({ keyleds.KEY_MENU: do_abort})
    await kernel(v)