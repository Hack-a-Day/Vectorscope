
from vectorscope import Vectorscope
import vectoros
import keyboardcb
import keyleds
import asyncio

import random_walk 

_abort=False

async def random_walker(v):
    ## Minimal example
    global _abort
    r = random_walk.RW(v)
    x,y = 0,0
    while _abort==False:
        x,y = r.random_walk(x,y)
        ## this is important -- it yields to the key scanner
        await asyncio.sleep_ms(10)
            
## Below here is boilerplate.  
def do_abort(key):
    global _abort
    _abort=True
    
from vos_state import vos_state

async def slot_main(v):
    global _abort
    # watch the keys -- you can define your own callbacks here
    mykeys = keyboardcb.KeyboardCB( {keyleds.KEY_MENU: do_abort} )
    await random_walker(v)
    print("OK done")
