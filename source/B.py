
import math
import time

from vectorscope import Vectorscope

import vectoros
import keyboardcb
import keyleds
import asyncio


_abort=False
_xscale=1
_yscale=1

async def kminimal_example(v):
    ## Minimal example with keys
    global _abort, _xscale, _yscale
    while _abort==False:
        for i in range(360):
            scale=1
            if _abort:
                print("Get out!")
                break
            v.wave.constantX(int(math.cos(i * math.pi / 180 * 5*_xscale) * 10000))
            v.wave.constantY(int(math.sin(i * math.pi / 180 * 5*_yscale)* 10000))
            await asyncio.sleep_ms(10)
            

def do_abort(key):
    global _abort
    _abort=True
    
def do_xscale(key):
    global _xscale
    _xscale+=1
    if _xscale>6:
        _xscale=1
    

def do_yscale(key):
    global _yscale
    _yscale+=1
    if _yscale>6:
        _yscale=1
    


from vos_state import vos_state

async def slot_main(v):
    global _abort,_continue
# So... Press D (or whatever is configured) and note the message below. Press Range to start the demo
# The demo will run until you press Menu. LEVEL/RANGE will change frequency of X and Y in steps
# Note that if you don't yield occasionaly, you don't get key scanning

    # watch the keys
    mykeys=keyboardcb.KeyboardCB({ keyleds.KEY_LEVEL: do_xscale, keyleds.KEY_RANGE: do_yscale, keyleds.KEY_MENU: do_abort})


    await kminimal_example(v)
    print("OK done")
