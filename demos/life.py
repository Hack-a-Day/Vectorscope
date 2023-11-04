import vectoros
from screennorm import ScreenNorm
import keyboardcb
import asyncio
import colors
import gc
import random
import keyleds


screen=None
pop=0
_exit=False
reseed=True

# take a line from the algorithm and plot it on the screen
def line(n, string):
    global pop
    pixsize=9
    corner=30
    if n==0:
       gc.collect()
       screen.clear(0)
       pop=0
    x=corner
    y=pixsize*n+corner
    for c in string:
        if c=='*':
            screen.tft.fill_rect(x,y,pixsize,pixsize,colors.PHOSPHOR_DARK)
            pop+=1
        x+=pixsize


# Range button does a reseed
def do_reseed(key=None):
    global reseed
    reseed=False
    rlist=[]
    n=random.randint(15,40)
    for i in range(n):
        rlist.append(random.randint(0,399))
    return rlist


def do_exit(key):
    global _exit
    _exit=True
    
def set_reseed(key):
    global reseed
    reseed=True

# adapted from https://codegolf.stackexchange.com/questions/3434/shortest-game-of-life
# the grid is 20x20 and the seed is the number of cells on counting from 0....400
# increasing in the X axis. So... 0, 1, 2, 3... 19 <new row> 20, 21, 22....
# in this case, we randomly generate it in do_reseed

async def vos_main():
    global pop
    N=range(20)
    key=keyboardcb.KeyboardCB({keyleds.KEY_MENU: do_exit,
                               keyleds.KEY_RANGE: set_reseed})
    while _exit==False:
        if reseed or pop==0:
            P=do_reseed()
        for i in N:
         line(i,''.join(' *' [i*20+j in P] for j in N))
         await asyncio.sleep_ms(0)
         Q=[(p+d)%400 for d in(-21,-20,-19,-1,1,19,20,21)for p in P]
         P=set(p for p in Q if 2-(p in P)<Q.count(p)<4)
    key.detach()
     
if __name__=="__main__":
    screen=ScreenNorm()
    screen.clear(0)
    keyboardcb.KeyboardCB.run(250)
    asyncio.run(vos_main())