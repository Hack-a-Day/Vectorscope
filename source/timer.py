import vos_launch
import asyncio
import vos_debug


# if you don't care about the asyncio aspect of this
# you can try using machine.Timer 


class Timer:
    """
    A class that manages a timer for VectorOS.

    Attributes:
        clients (dict): Each item is [reset value, value, callback, sync/async, oneshot].
        baserate (int): The base rate in milliseconds.
        _next_id (int): The next id to use.
        current_id (int): The current id.
        task (Task): The task for the timer.
        gc_delay (int): The delay for garbage collection.
    """
    
    clients={}    
    baserate=vos_launch.timer_base_rate  
    _next_id=1
    current_id=None
    task=None
    gc_delay=0
    _cancel=False
    
    @classmethod
    async def _run(cls):
        """
        Class method to run the class level "server".

        Returns:
            Task: The created task.
        """
        
        cls.task=asyncio.create_task(cls._job())
    
    @classmethod
    def run(cls):
        """
        Class method to launch the event loop without having to create a task yourself.

        Returns:
            Task: The created task.
        """
        
        return asyncio.create_task(cls._run())
    
    @classmethod
    async def _job(cls):
        """
        Class method for the actual polling task.

        This method runs a loop that sleeps for a specified timeout and then ticks the timer.

         Returns:
            Task: The created task.
         """
        
        ctr=0
        while cls._cancel==False:
             await asyncio.sleep_ms(cls.baserate)
             await cls._tick()
             ctr+=1
             if cls.gc_delay!=0 and ctr>cls.gc_delay:
                 ctr=0
                 gc.collect()
        vos_debug.debug_print(vos_debug.DEBUG_LEVEL_INFO,"Timer exit")

    @classmethod
    def cancel(cls):
         """
         Class method to cancel the polling task.
         """
         cls._cancel=True
         cls.task.cancel()            

    @classmethod
    async def _tick(cls):
        """
        Class method to tick the timer.

        This method ticks the timer and calls the appropriate callback function for each timer event.
         """
        
        for item in cls.clients:
             cls.clients[item][1]+=1                             
             if cls.clients[item][0]<=cls.clients[item][1]:      
                 cls.clients[item][1]=0                          
                 cls.current_id=item
                 try:
                      await cls.clients[item][2]() 
                 except TypeError:
                    pass
                 try:
                     if cls.clients[item][3]:
                         del cls.clients[item]                       
                 except Exception:
                     pass
        cls.current_id=None
                    
    @classmethod
    def remove_timer(cls,id):
        """
        Class method to remove a timer.

        Args:
            id (int): The id of the timer to remove.
        """
        if id in cls.clients:
            cls._next_id=id     # try to recycle timer IDs (note we search "up" if one is in use already)
            del cls.clients[id]
        
    @classmethod
    def add_timer(cls,ticks, callback, oneshot=False):
        """
        Class method to add a timer.

        Args:
            ticks (int): The number of ticks before the timer triggers.
            callback (function): The function to call when the timer triggers.
            oneshot (bool): A flag to indicate if the timer should only trigger once. Default is False.

         Returns:
            int: The id of the added timer.
         """
        
        # we search for a free timerID starting from _next_id
        # normally that means we get an ascending number
        # but if you delete a timer ID we will reuse it unless
        # you delete two or more without creating any
        # then you may "leak" lower number IDs but you
        # should run out of resources before you run out of IDs
        # anyway This is just a hedge for the case where you
        # constantly create/remove a timer
        while cls._next_id in cls.clients:            
             cls._next_id+=1   
             
        rv=cls._next_id
        cls.clients[cls._next_id]=[ticks,0,callback,oneshot]
        cls._next_id+=1
         
        return rv
  
    def __init__(self,ticks,paused=False,oneshot=False):
        """
        The constructor for Timer class.

        Args:
            ticks (int): The number of ticks before the timer triggers.
            paused (bool): A flag to indicate if the timer should start paused. Default is False.
            oneshot (bool): A flag to indicate if the timer should only trigger once. Default is False.
         """
        
        self.ticks=ticks
        self.paused=paused
        self.oneshot=oneshot
        
        if paused:
            self.id=None
        else:
            self.id=self.add_timer(ticks,self.action,oneshot)
        
    def __enter__(self):
         return 
        
    def __exit__(self,exc_type,exc_val,exc_tb):
         if self.id!=None:
             self.remove_timer(id)
    
    def action(self):
         print("unhandled action")
    
    def pause(self):
         if self.id==None:
             return   
         
         try:
             self.remove_timer(self.id)
         except Exception:
             pass
         
         finally:
             self.id=None 
    
    def resume(self):
         try:
             self.remove_timer(self.id)
         except Exception:
             pass
         
         self.id=self.add_timer(self.ticks,self.self.action,True,self.oneshot)
         
         return self.id
        
if __name__=="__main__":
    import gc
    onesecid=0
    
    Timer.gc_delay=500
    
    class Test(Timer):
        def __init__(self):
            super().__init__(20)
            self.ct=0
            
        def action(self):
            self.ct=self.ct+1
            print("**",self.ct)
            if (self.ct>=10):
                self.pause()
                
        
    twosec = Test()
       

    def callback1sec():
        """
        Function to print a message every second.
        """
        
        print("Tick 1")
        
    def callback5sec():
        """
        Function to print a message and the amount of free memory every 5 seconds.
        """
        
        print("Tick 5",gc.mem_free())

    def once():
        """
        Function to print a message and remove the 1 second tick. This function only runs once.
        """
        
        global onesecid
        print("I only run once",onesecid)
        Timer.remove_timer(onesecid)

    async def acallback_worker():
        """
        Asynchronous function to print a start and end message with a delay of 5 seconds.
        """
        
        print("async start")
        await asyncio.sleep(5)
        print("async done")
    
    # This is an async callback. However, the timer will stall until it completes
    # so we just kick off a new task to run in the background and then the timer does its thing
    async def acallback():
        asyncio.create_task(acallback_worker())
    
    async def amain():
        """
        Asynchronous main function to run the timer and add several tasks to it.
        """
        
        global onesecid
        Timer.run()
    
        
        onesecid=Timer.add_timer(10,callback1sec)   # every one second
        Timer.add_timer(50,callback5sec)             # 5 second synchronous repeating
        Timer.add_timer(100,once,True)          # one shot and remove the 1 second tick
        Timer.add_timer(55,acallback,True)   # one shot
    
        while True:
            await asyncio.sleep(0)
            
    asyncio.run(amain())


