# list of things to launch from vectoros

# dictionary of tags to imports (will look for .vos_main() or .main() here) 
launch_list={ "menu": "supercon_menu", 'sketch': 'sketch', "demo": "examples", "planets":"planets", "lissajous":"lissajous"}

# list what you want to start auto (maybe just one thing?) need tag
auto_launch_list=["menu"]

vectorscope_slots={"slotA": "A", "slotB": "B", "slotC": "C", "slotD": "D"}

auto_launch_repl=False    # to get out: import sys followed by sys.exit()

key_scan_rate = 100    # how often to scan the keyboard globally (ms; 0 to do it yourself)

# how often to garbage collect
# if you set this to zero and do nothing else
# garbage collection will be automatic as usual and before new tasks launch
gc_thread_rate = 5000

# Base rate for the timer (ms)
timer_base_rate=100

# Debug level (messages must be < this level to print)
# That is, at level 0 only level 0 messages print
# at level 1 then level 1 and level 0 messages print
# Set level to -1 to stop all messages (assuming you only call debug_print with positive values)

# if you want to use symbols for debug level, these are defined in vos_debug:
DEBUG_LEVEL_SILENT=-1
DEBUG_LEVEL_SEVERE=0
DEBUG_LEVEL_ERROR=10
DEBUG_LEVEL_WARNING=20
DEBUG_LEVEL_INFO=30

debug_level=DEBUG_LEVEL_INFO


if __name__=="__main__":
    import vectoros
    vectoros.run()
