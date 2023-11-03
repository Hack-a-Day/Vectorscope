

DEBUG_LEVEL_SILENT=-1
DEBUG_LEVEL_SEVERE=0
DEBUG_LEVEL_ERROR=10
DEBUG_LEVEL_WARNING=20
DEBUG_LEVEL_INFO=30

from vos_launch import debug_level

def debug_print(level,*args):
    """
    Function to print debug messages that are lower than debug level (set in vos_launch.py)
    """
    if level<=debug_level:
        return print(*args)
    