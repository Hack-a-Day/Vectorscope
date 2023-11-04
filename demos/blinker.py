import vectoros
import asyncio
import keyleds
import keyboardio
import timer
import vos_debug

_freeze=False
_exit=False

def exit():
    """
    Function to exit the current task.
    """
    global _exit
    _exit=True
    vectoros.remove_task('blinky')

def freeze(state=True):
    """
    Function to freeze the blinking of LEDs.

    Args:
        state (bool): True to freeze, False to unfreeze. Default is True.
    """
    global _freeze
    _freeze=state

def callback1500ms():
    """
    Callback function that is called every 1500ms.
    """
    global _freeze
    if _freeze:
        return 
    v=keyboardio.KeyboardIO.leds
    v^=0xF0
    keyboardio.KeyboardIO.leds=v

async def test_main():
    """
    Main function for the VectorOS.

    This function runs a loop until the exit flag is set to True. 
    It controls the LED states using the KeyboardIO object.
    """
    global _freeze, _exit
    _freeze=False
    _exit=False
    if vectoros.vectoros_active()==False:
        keyboardio.KeyboardIO.run(250)
    timertask=timer.Timer.add_timer(15,callback1500ms)
    while _exit==False:
        if _freeze==False:
            keyboardio.KeyboardIO.leds=(keyboardio.KeyboardIO.leds&0xF0)|0xA
        await asyncio.sleep_ms(500)
        if _freeze==False:
            keyboardio.KeyboardIO.leds=(keyboardio.KeyboardIO.leds&0xF0)|5
        await asyncio.sleep_ms(500)
    
    _exit=False
    timer.Timer.remove_timer(timertask)
    vectoros.remove_task('blinky')
    vos_debug.debug_print(vos_debug.DEBUG_LEVEL_INFO,"Blinky exiting")

# I use this to test running a  main instead of vos main.
async def main():
    """
    Function to start the blinking of LEDs.
    
    This function runs the main VectorOS function in an event loop.
    """
    await test_main()

if __name__=="__main__":
    main()
