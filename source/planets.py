# A little slideshow you can customize

import screennorm
import keyboardcb
import keyleds
import vectoros
import timer
import gc
import asyncio
from vos_state import vos_state
import colors


screen=screennorm.ScreenNorm()   # get the screen



current_slide=0   # current slide
exit_flag=False   # don't exit
tid=None          # timer ID
timer_rate=100    # timer rate (ticks; see vos_launch.py for multiplier)
pauseflag=False   # pause slide show

# comamnds for slides
TEXT=0
IMAGE=1
BACKGROUND=2
TEXTXY=3

slides=[
        [ IMAGE, "pl_mercury.jpg" ],
        [ IMAGE, "pl_venus.jpg" ],
        [ IMAGE, "pl_earth.jpg" ],
        [ IMAGE, "pl_moon.jpg" ],        
        [ IMAGE, "pl_mars.jpg" ],
        [ IMAGE, "pl_jupiter.jpg" ],
        [ IMAGE, "pl_saturn.jpg" ],
        [ IMAGE, "pl_uranus.jpg" ],
        [ IMAGE, "pl_neptune.jpg" ],
       ]

# get next slide
def next():
    global current_slide, TEXT, IMAGE
    bkflag=False
    if pauseflag:
        return  # nothing doing
    cmdlist=slides[current_slide]
    if cmdlist[0]==IMAGE or cmdlist[0]==BACKGROUND:
        screen.jpg(cmdlist[1])
    if cmdlist[0]==BACKGROUND:
        bkflag=True
        current_slide+=1
        if current_slide>=len(slides):
            current_slide=0
        cmdlist=slides[current_slide]   #assume next one will be TEXT
    if cmdlist[0]==TEXT:
        x=40
        y=40
    if cmdlist[0]==TEXTXY:
        x=cmdlist[1]
        y=cmdlist[2]
        cmdlist[0]=TEXT
        del cmdlist[1:3]
        
    if cmdlist[0]==TEXT:
        if bkflag==False:
            screen.clear(cmdlist[2])
        for txt in cmdlist[3:]:
            screen.text(x,y,txt,cmdlist[1], cmdlist[2])
            y+=30
    current_slide+=1   # advance slide
    if current_slide>=len(slides):
        current_slide=0   # or recycle


# if you change the timeout we have to kill the old timer and make a new one
def update_timer():
    global tid, timer_rate
    timer.Timer.remove_timer(tid)
    tid=timer.Timer.add_timer(timer_rate,next)  # change over

# Joystick
# Up is delay up, Down is delay down
# Right is next, and Left toggles the pause flag
def joycb(key):
    global timer_rate, pauseflag
    if (key==keyleds.JOY_UP):
        timer_rate+=10
        if timer_rate>200:
            timer_rate=200
        update_timer()
    if (key==keyleds.JOY_DN):
        timer_rate-=10
        if timer_rate<=0:
            timer_rate=1
        update_timer()
    if (key==keyleds.JOY_RT):
        oldpause=pauseflag
        pauseflag=False   # make sure it redraws
        next()
        pauseflag=oldpause
    if (key==keyleds.JOY_LF):
        pauseflag=not pauseflag



    
def menu(key):						# menu -bail out
    global exit_flag
    exit_flag=True





async def vos_main():
    global exit_flag, current_slide, tid, timer_rate
    current_slide=0
    # we treat the joystick like any other key here
    keys=keyboardcb.KeyboardCB({keyleds.KEY_MENU: menu, keyleds.JOY_UP: joycb, keyleds.JOY_DN: joycb, keyleds.JOY_RT: joycb, keyleds.JOY_LF: joycb})
    tid=timer.Timer.add_timer(timer_rate,next)
    # prime it
    next()
    # do nothing... everything is on keyboard and timer
    while exit_flag==False:
        await asyncio.sleep_ms(500)
# stop listening for keys
    keys.detach()
    timer.Timer.remove_timer(tid)
    exit_flag=False  # next time

    vos_state.show_menu=True  # tell menu to wake up
    


if __name__=="__main__":
    import vectoros
    vectoros.run()
