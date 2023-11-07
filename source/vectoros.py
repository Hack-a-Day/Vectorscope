import aiorepl
import asyncio
import keyboardio
import screennorm
import timer
from vos_launch import launch_list, auto_launch_list, auto_launch_repl, key_scan_rate, gc_thread_rate, timer_base_rate, vectorscope_slots
from vos_state import vos_state
import gc
from machine import RTC
from machine import reset as m_reset, soft_reset as m_soft_reset
import vos_debug



_VERSION=20231101

_screen=screennorm.ScreenNorm()


async def _sleeper():
    """
    Asynchronous function to sleep forever.

    This function runs a loop that sleeps for 5 seconds and then collects garbage.
    """
    
    while True:
        await asyncio.sleep_ms(gc_thread_rate)
        if vos_state.gc_suspend==False:
            gc.collect()

def reset():
    m_reset()
    
def soft_reset():
    m_soft_reset()


def sleep_forever():
    """
    Function to let non async function wait forever.
    """
    
    asyncio.run(_sleeper())

async def _delayer(n):
    """
    Asynchronous function to delay for n seconds.

    Args:
        n (int): The number of milliseconds to delay.
    """
    
    await asyncio.sleep_ms(n)

def sleep(n):
    """
    Function to delay for n seconds.

    Args:
        n (int): The number of milliseconds to delay.
    """
    vos_debug.debug_print(vos_debug.DEBUG_LEVEL_WARNING,"sleep called which uses asyncio.run")
    asyncio.run(_delayer(n))

def get_screen():
    """
    Function to get the one screen object.

    Returns:
        ScreenNorm: The screen object.
    """
    
    global _screen
    return _screen

async def launch_repl():
        """
        Asynchronous function to start a repl.
        """
        
        vos_state.task_dict['$repl']=asyncio.create_task(aiorepl.task())

async def launch(task_tag):
    """
    Asynchronous function to launch a program by its tag.

    Args:
        task_tag (str): The tag of the program to launch.
        
     Returns:
            Task: The created task.
     """
    if vos_state.gc_suspend==False:
         gc.collect()
    vos_debug.debug_print(vos_debug.DEBUG_LEVEL_INFO,f"launching {task_tag}")
    mod=__import__(launch_list[task_tag])
    try:
        fn=getattr(mod,'vos_main')
    except Exception:
        vos_debug.debug_print(vos_debug.DEBUG_LEVEL_WARNING,f"launch could not find vos_main for {task_tag}. Trying main()")
        fn=getattr(mod,'main')
    try:
        await fn()
    except TypeError:
        pass

        

def launch_task(task_tag):
     """
     Function to create async task to launch.

     Args:
         task_tag (str): The tag of the program to launch.
         
      Returns:
            Task: The created task.
      """
     vos_state.task_dict[task_tag]=asyncio.create_task(launch(task_tag))
     
     
async def launch_vecslot(slot):
    from vectorscope import Vectorscope
    _screen.clear()
    _screen.idle()
    gc.collect()
    vos_state.gc_suspend=True
    vos_state.show_menu=False 
    vos_debug.debug_print(vos_debug.DEBUG_LEVEL_INFO,f"Launching slot {slot}:{vectorscope_slots[slot]}")
    mod=__import__(vectorscope_slots[slot])
    fn=getattr(mod,'slot_main')
    v = Vectorscope(screen_running=True)
    try:
        vos_debug.debug_print(vos_debug.DEBUG_LEVEL_INFO,"launching")
        await fn(v)
    except TypeError:
        pass
    except Exception as e:
        print("launch exception",e)
    finally:
        vos_debug.debug_print(vos_debug.DEBUG_LEVEL_INFO,"Slot done, reboot!")
#        await asyncio.sleep(5)
        reset()
    
    
def remove_task(t):   
     """
     Function to remove a task. Note that this does not stop the task, just takes it out of the list

     Args:
         t (str): The tag of the task to remove.
      """
     
     try:   
         vos_state.task_dict.pop(t)
     except Exception:
         pass

_gc_exit=False

async def _gc_thread(ms):
     """
     Asynchronous function for optional thread to garbage collect occasionally.

     Args:
         ms (int): The number of milliseconds to sleep between garbage collections.
      """
     global _gc_exit
     while _gc_exit==False:
         await asyncio.sleep_ms(ms)
         if vos_state.gc_suspend:
             continue
         vos_debug.debug_print(vos_debug.DEBUG_LEVEL_INFO,"Garbage collection starting")
         gc.collect()
         gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
     vos_debug.debug_print(vos_debug.DEBUG_LEVEL_INFO,"Garbage collection thread exit")


def vectoros_active():
     """
     Function to test if we are active.

     Returns:
         bool: True if active, False otherwise.
      """
     
     return vos_state.active
    
_vectoros_runafter=None

def set_global_exception():
     """
     Function to catch exceptions. 
      """
     def handle_exception(loop,context):
         import sys
         if context["exception"].args[0]=="__vectoros-exit__":
             vos_state.run_after=context["exception"].args[1]
         else:
             sys.print_exception(context["exception"])
         sys.exit()

     
     loop=asyncio.get_event_loop()
     loop.set_exception_handler(handle_exception)
     
async def vectoros_startup(autolaunch=True):
    """
    Function to start services (called by main)
    
    Args:
    autolaunch (bool): True to launch autostart programs (default)
    """
    global _VERSION
    vos_state.version=_VERSION
    vos_debug.debug_print(vos_debug.DEBUG_LEVEL_INFO,f"VectorOS {_VERSION} starting",RTC().datetime())
# honor gc thread request    
    if gc_thread_rate!=0:
        gc.disable()
        vos_state.task_dict['$gc']=asyncio.create_task(_gc_thread(gc_thread_rate))
# spin up system-level keyboard polling (see keyboardcb and joystick)
    if key_scan_rate!=0:
        vos_state.task_dict['$key']=keyboardio.KeyboardIO.run(key_scan_rate)
# spin up timer infrastructure
    if timer_base_rate!=0:
        vos_state.task_dict['$timer']=timer.Timer.run()
# at this point, we consider ourselves running        
    vos_state.active=True
# launch repl if requested
    if autolaunch:
        if (auto_launch_repl):
            await launch_repl()
# run auto launch stuff from vos_launch        
        for t in auto_launch_list:
            vos_state.task_dict[t]=asyncio.create_task(launch(t))
        vos_debug.debug_print(vos_debug.DEBUG_LEVEL_INFO,"VectorOS started",RTC().datetime())
            

# shut down our service (but not apps)
def vectoros_shutdown(deactivate=True):
    """
    Function to shut down vectoros services
    """
    global _screen, _gc_exit
    vos_debug.debug_print(vos_debug.DEBUG_LEVEL_INFO,"VectorOS shutting down",RTC().datetime())
    _screen.idle()
    _screen=None
    keyboardio.KeyboardIO.cancel()
    del vos_state.task_dict['$key']
    timer.Timer.cancel()
    del vos_state.task_dict['$timer']
    _gc_exit=True
#    vos_state.task_dict['$gc'].cancel()
    del vos_state.task_dict['$gc']
    for x in vos_state.task_dict:
        vos_state.task_dict[x].cancel()
    if (deactivate):
        vos_state.active=False
    asyncio.get_event_loop().set_exception_handler(None)
    gc.collect()
    vos_debug.debug_print(vos_debug.DEBUG_LEVEL_INFO,"VectorOS shut down",RTC().datetime())
    
def ext_run(cmd):
    """
    Function to exit VectorOS and run a program
    """
    gc.collect()
    vos_debug.debug_print(vos_debug.DEBUG_LEVEL_INFO,f"external run {cmd}")
    raise Exception("__vectoros-exit__",cmd)



# get all set up
async def main():
    """
    Asynchronous main function to set up the system.

    This function sets up exception handling, starts the garbage collection thread, keyboard polling, and timer infrastructure,
    launches the repl if requested, imports modules from vos_launch, and runs auto launch stuff from vos_launch.
    """
# catch any strange exceptions
    set_global_exception()
    await vectoros_startup()
    await _sleeper()
    
# This is the main entry point that starts everything    
def run():
    """
    Function to run the main function.

    This function runs the main function and resets the event loop.
    """
    global _vectoros_runafter, _vectoros_runaftermod
    cmd=None
    while True:
        try:
            asyncio.run(main()) # do not create tasks before this point!
        except SystemExit as se:
            break    # catch sys.exit
        except Exception as e:
            print(e)                        # shouldn't really run
            print(hasattr(e,'arg'))
            if hasattr(e,'arg'):
                if e.arg[0]=='__vectoros-exit__':
                    _vectoros_runafter=e.args[1]
                else:
                    print(e)
            else:
                print(e)
# This code launches a program after vectoros shutdown
# The "single core" method works more reliably but if it is
# in the second core causes stack errors (vos_state._xthreading==0)
# The vos_state._xthreading==1 case works for multicore but
# requrires a small server on the main core
#This mostly works in single core mode
        finally:
            if vos_state._xthreading==0:      # single core mode 
                if vos_state.run_after != None:					# as we exit, set up any pending command
                    cmd=vos_state.run_after
                    vos_state.run_after=None
                else:
                    vos_debug.debug_print(vos_debug.DEBUG_LEVEL_INFO,"reset event loop")
                    asyncio.new_event_loop()
                if cmd!=None:
                     vectoros_shutdown()
                     vos_state.gc_suspend=True
                     asyncio.sleep_ms(250)   # hope the gc thread dies if it hasn't already
                     import sys
                     del sys.modules['screennorm']
                     del sys.modules['aiorepl']
                     del sys.modules['romans']
                     del sys.modules['vga1_16x32']
                     gc.collect()
                     exec(cmd)
            else:                        # multicore mode (requires start w/split_vos.py)
                if vos_state.run_after != None:					# as we exit, set up any pending command
                    print("core 1 passing back to zero")
                    import sys
                    del sys.modules['screennorm']
                    del sys.modules['aiorepl']
                    del sys.modules['romans']
                    del sys.modules['vga1_16x32']
                    del sys.modules['keyboardio']
                    del sys.modules['timer']
                    vos_state.gc_suspend=True
                    asyncio.sleep_ms(250)   # hope the gc thread dies if it hasn't already
                    gc.collect()
                    vectoros_shutdown(False)
                    gc.collect()
                else:
                    print("Resetting event loop")
                    asyncio.new_event_loop()
    if vos_state._xthreading==1:
       gc.collect()
       vos_state.active=False
    else:
        pass

if __name__=="__main__":
    run()


    
    
        
