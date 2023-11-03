import joystick
from menu import *   # bad habit but makes our menu definition nice
from vos_state import vos_state
import blinker
import vectoros
import colors
import gc 

# run the sketch demo
def runsketch(arg):
    vos_state.show_menu=False     # get the menu of the way
    vectoros.launch_task('sketch')
    return EXIT

def gfxdemo(arg):
    vos_state.show_menu=False     # get the menu of the way
    vectoros.launch_task('screen')  # launch
    return EXIT

def testdemo(arg):
    import tester2
    vectoros.vectoros_shutdown()
    tester2.main()   # this never returns but it does reboot


# the main vector scope demo
def run_demo(arg):
    vos_state.show_menu=False
    vectoros.launch_task('demo')  
    # we never come back
    return EXIT

def reboot(arg):
    if arg==False:
        vectoros.reset()
    else:
        vectoros.soft_reset()

# handle slots
def abcd(key):
    if vos_state.show_menu:
        vos_debug.debug_print(vos_debug.DEBUG_LEVEL_INFO,f"Menu key {key}")
        kdict={ keyleds.KEY_A: 'A', keyleds.KEY_B: 'B', keyleds.KEY_C: 'C', keyleds.KEY_D: 'D'}
        await vectoros.launch_vecslot("slot"+kdict[key])
    

# I really didn't want this to be async but it seems like do_menu must have an await
# and run rarely returns when you have a lot going on
async def vos_main():
# you do NOT have to use with here
# but if you don't you have to worry about the menu controller's joystick instance going out of scope yourself
# or just make everything global -- the menu is smart enough to not listen to events when it is not active
# note: m_back and m_exit were imported from menu
    while True: # since this is the main menu, we don't really every quit
        print("creating slotkey")
        slotkey=keyboardcb.KeyboardCB(abcd,keyleds.KEY_ABCD)
        with Menu(clear_after=True,fg_color=colors.PHOSPHOR_DARK,bg_color=colors.PHOSPHOR_BG,
                  cursor_bg=colors.PHOSPHOR_BG, cursor_fg=colors.PHOSPHOR_BRIGHT) as amenu:  
            # submenu=[["Test", testdemo, 0],["Previous",m_back,None],["Abort",m_exit,None],["Reset CPU",reboot,False]]
            mainmenu=[["Demo",run_demo,None],["Sketch", runsketch, 0],["GFX",gfxdemo,0 ] ]
                    #  ["Test Menu",SUBMENU,submenu]]
# comment next line for default font
            amenu.set_font("*")   # set default vector font
            #amenu.set_callback(menu_custom)
            await amenu.do_menu(mainmenu)
#    screen.text(40,80,"menu done")
        vos_debug.debug_print(vos_debug.DEBUG_LEVEL_INFO,f"Menu waiting {vos_state.show_menu}")
        while vos_state.show_menu==False:   # wait until we have to be seen again
            await asyncio.sleep_ms(0)
    

def main():
    asyncio.run(vos_main())
    # this never runs 

if __name__=="__main__":
    import vectoros
    vectoros.run()
    
