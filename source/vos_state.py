# state for vector os

class vos_state:
    task_dict={}  # tasks created (not removed, though, unless you do it yourself
    active=False   # are we active?
    gc_suspend=False  # do you want to suspend the gc? 
    show_menu=True    # Used to restart main menu
    run_after=None    # Run after OS is done
    version=None      # Version (filled in on init)
    _xthreading=0
    
    
# put any globals you want for your application here (nice to put them "in" something like a dictionary

# global my_task_vars={"exit_flag": False, "rate": 200}


    