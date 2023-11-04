# Almost the simplest VectorOS program:

import vectoros
import keyleds
import keyboardio
from timer import Timer



task_name="Simple"  # use this name in vos_launch.py, too
_run_every_ms=500   # how often to loop


_freeze=False
_exit=False
_timerid=None


# Outsiders can call this to exit you
def exit():
    global _exit,task_name
    _exit=True
    vectoros.remove_task(task_name)


# Outsiders can call this to pause you
def freeze(state=True):
    global _freeze
    _freeze=state


def callback():
    global _exit, _freeze, _timerid
    if _exit:
        Timer.remove_timer(_timerid)
        return 
    if _freeze==False:
        keyboardio.KeyboardIO.leds^=0xFF
    

def main():
    Timer.add_timer(5, callback)   # 5 * 100 = 500 ms
    vectoros.sleep_forever()
    
# code here will never, ever run under VectorOS

# if you want the possibility to run directly without VectorOS
#if __name__=="__main__":
#    main()

# if you want to configure to run in vos_launch but still run this file
# add the main function to to vos_launch.py and use this:
if __name__=="__main__":
    vectoros.run()
