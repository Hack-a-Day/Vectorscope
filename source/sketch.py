import screennorm
import keyboardcb
import keyleds
import joystick
import vectoros
from vos_state import vos_state
import gc9a01

# little etch-a-sketch demo

pendown = True           # start off with pen down
color = gc9a01.BLACK     # start off black

# To maintain the cursor we need a bit map which is slow
# so less is more. Also pixels are tiny
# so 40 is a good compromise (40x40 drawing area)
SIZE=40     
PIXSIZE=240//SIZE            # size of each "pixel"

# start cursor in the middle
cursor_x = (SIZE+1)//2
cursor_y = (SIZE+1)//2

# This will be the backing store for the screen
model=[]

stopflag=False  # stop when true

# clear the mdoel with color c (does not draw; see cursor)
def fill_model(c):
    global model
    model=[[c for i in range(SIZE)] for j in range(SIZE)]



# update screen and overlay cursor (or just cursor area if blit==False)
def cursor(blit=True):
    global model
    global cursor_x
    global cursor_y
    global PIXSIZE
    global pendown
    ccolor=gc9a01.color565(0xC0,0xFF,0x80)
    if pendown:
        ccolor=gc9a01.color565(0xFF,0x80,0x80)
    if blit:
        for x in range(SIZE):
            for y in range(SIZE):
                screen.tft.fill_rect(x*PIXSIZE,y*PIXSIZE,PIXSIZE,PIXSIZE,model[x][y])
    else:  # only draw around the cursor
        for x in range(-1,2):
            for y in range(-1,2):
                nx=cursor_x+x
                ny=cursor_y+y
                screen.tft.fill_rect(nx*PIXSIZE,ny*PIXSIZE,PIXSIZE,PIXSIZE,model[nx][ny])
    screen.tft.fill_rect(cursor_x*PIXSIZE,cursor_y*PIXSIZE,PIXSIZE,PIXSIZE,ccolor)

# flip pen/up down on joystick button (non-repeating)
def joybtn(key):
    global pendown
    pendown=not pendown
    cursor(False)   # update cursor color

# normal joystick commands
def joycmd(key):
    global pendown, cursor_x, cursor_y
    x=0
    y=0
    if key==keyleds.JOY_N:
        y=-1
    elif key==keyleds.JOY_S:
        y=1
    elif key==keyleds.JOY_E:
        x=1           
    elif key==keyleds.JOY_W:
        x=-1
    elif key==keyleds.JOY_NW:
        y=-1
        x=-1
    elif key==keyleds.JOY_SW:
        y=1
        x=-1
    elif key==keyleds.JOY_NE:
        y=-1
        x=1
    elif key==keyleds.JOY_SE:
        y=1
        x=1
    if x!=0 or y!=0:
        newx=cursor_x+x
        if newx>=0 and newx<SIZE-1:
            cursor_x=newx
        newy=cursor_y+y
        if newy>=0 and newy<SIZE-1:
            cursor_y=newy
        if pendown:
            model[cursor_x][cursor_y]=color
        cursor(False)

# command keys (A=Black, B=Red, C=Green, D=Blue, User=Clear)
def red(key):
    global color
    color=gc9a01.RED
    
def green(key):
    global color
    color=gc9a01.GREEN
    
def blue(key):
    global color
    color=gc9a01.BLUE 
    
def black(key): 
    global color
    color=gc9a01.BLACK
def white(key):   # erase
    global color
    color=gc9a01.WHITE

def cls(key):
    fill_model(gc9a01.WHITE)
    cursor()

def menu(key):       # exit and return to menu
    global stopflag
    print("menu")
    if vos_state.active:
        stopflag=True
        joy.detach()
        btn.detach()
        csel.detach()

# create our screen and keyboard/joystick
screen=screennorm.ScreenNorm()
joy=joystick.Joystick(joycmd,attach=False)
btn=keyboardcb.KeyboardCB(joybtn,keyleds.JOY_PRESS,attach=False)  # no repeat
csel=keyboardcb.KeyboardCB({ keyleds.KEY_LEVEL: white, keyleds.KEY_A: black,
                             keyleds.KEY_B: red, keyleds.KEY_C: green, keyleds.KEY_D: blue, keyleds.KEY_USER: cls,
                             keyleds.KEY_MENU: menu},
                           attach=False)
                             

import asyncio
import gc

async def vos_main():
    global stopflag
    if keyboardcb.KeyboardCB.task==None:
        keyboardcb.KeyboardCB.run(100)  # start keyboard service
    cls(None)                 # zero out model and draw
    joy.attach()
    btn.attach()
    csel.attach()

    while stopflag==False:
        await asyncio.sleep(5)
        if vos_state.active==False:
            gc.collect()
    stopflag=False   # ready for next time
    vos_state.show_menu=True
    vectoros.remove_task('sketch')
    print("Exiting")


def main():
    asyncio.run(vos_main())

if __name__ == "__main__":
    main()
