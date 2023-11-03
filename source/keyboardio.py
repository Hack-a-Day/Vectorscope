import asyncio
import keyleds
from machine import SoftSPI, Pin
import vos_debug

class KeyboardIO:
    """
    A class that reads keys from the board and manages LEDs. 

    Attributes:
        leds (int): The LEDs to write out.
        task (Task): The task for the keyboard polling loop.
        current_keys (list): The list of currently pressed keys.
        _timeout (int): The poll rate in ms.
        _spi (SoftSPI): The SPI interface.
        _latch_load (Pin): The shift-register load pin.
        _button_sense (list): The two columns of button matrix.
        _user_sense (Pin): The user sense pin.
        _subscribers (list): The list of subscribers who want to know about keys.
        _prev (list): The list of keys that were down in the last poll.
        _capture (KeyboardIO): The subscriber that hogs all the keyboard.
    """
    
    leds=0   
    task=None          
    current_keys=[]   

    _timeout=100  
    _spi = SoftSPI(baudrate=500_000,  sck=Pin(0), mosi=Pin(1), miso=Pin(19)) 
    _spi.init()
    _latch_load = Pin(16, mode=Pin.OUT, value=0)                     
    _button_sense = [Pin(17, mode=Pin.IN), Pin(18, mode=Pin.IN)] 
    _user_sense = Pin(19, mode=Pin.IN)  
    _subscribers=[]    
    _prev=[]           
    _capture=None
    _cancel=False

    def __init__(self, attach=True):
        """
        The constructor for KeyboardIO class.

        Args:
            attach (bool): A flag to indicate if the keyboard should be attached during initialization. Default is True.
        """
        
        self.subref=self.key 
        if (attach):
            self._subscribers.append(self.subref);

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._capture==self.subref:
            self._capture=None
        self.detach()

    def capture(tf=True):
        """
        Function to grab all keyboard events for this instance.

        Args:
            tf (bool): A flag to indicate if the keyboard events should be captured. Default is True.

        Returns:
            bool: True if the capture was successful, False otherwise.
        """
        
        if tf==True and self._capture!=None and self._capture!=self.subref:
            return false
        if tf==False and self._capture!=self.subref:
            return false
        if tf==True:
            self._capture=self.subref
        else:
            self._capture=None 
        return True 

    @classmethod
    async def _run(cls, timeout_ms=100):
        """
        Class method to run the class level "server".

        Args:
            timeout_ms (int): The timeout in ms. Default is 100.

        Returns:
            Task: The created task.
        """
        
        if timeout_ms!=0:
            cls._timeout=timeout_ms
        cls.task=asyncio.create_task(cls._job())
    
    @classmethod
    def run(cls,timeout_ms=100):
        """
        Class method to launch the event loop without having to create a task yourself.

        Args:
            timeout_ms (int): The timeout in ms. Default is 100.

        Returns:
            Task: The created task.
        """
        
        return asyncio.create_task(cls._run(timeout_ms))
    
    @classmethod
    async def _job(cls):
        """
        Class method for the actual polling task.
        
        This method runs a loop that sleeps for a specified timeout and then scans the keyboard.
        
         Returns:
            Nothing
        """
        vos_debug.debug_print(vos_debug.DEBUG_LEVEL_INFO,"Starting keyboard loop")
        while cls._cancel==False:
             await asyncio.sleep_ms(cls._timeout)
             await cls._do_scan()
        vos_debug.debug_print(vos_debug.DEBUG_LEVEL_INFO,"KEYIO exiting")

    @classmethod
    def cancel(cls):
         """
         Class method to cancel the polling task.
         """
         cls._cancle=True
         cls.task.cancel()
    
    def attach(self):
         """
         Method to attach a subscriber to the keyboard.

         This method adds a subscriber to the list of subscribers if it is not already there.
         """
         
         if self.subref not in self._subscribers:  
             self._subscribers.append(self.subref)
    
    def detach(self):
         """
         Method to detach a subscriber from the keyboard.

         This method removes a subscriber from the list of subscribers if it is there.
         """
         
         if self.subref in self._subscribers:
             self._subscribers.remove(self.subref)

    @classmethod
    async def _do_scan(cls):
         """
         Class method to scan the keyboard and process all keys.

         This method scans the keyboard and calls the appropriate callback function for each pressed key.
         """
         b=cls.scan()
         if b!=[]:
             cls.current_keys=b
             if cls._capture==None:
                 for sub in cls._subscribers:
                     try:
                         await sub(b)
                     except TypeError:
                         pass
             else:
                 try:
                     await cls._capture(b)
                 except TypeError:
                     pass
             cls._prev=b
         else:
             cls._prev=[]


    @classmethod
    def scan(cls):
        """
        Class method to scan the buttons.

        This method scans the buttons and returns a list of pressed keys.

        Returns:
            list: The list of pressed keys.
        """
        
        buttons = []
        button_scan = 1
        if cls._user_sense()==0:
            buttons = [ 24 ]
        
        # update leds and scan buttons (if scan provided)
        for i in range(8):
            register = cls.leds + (button_scan << 8)
            cls._spi.write(register.to_bytes(2,'big'))
            cls._latch_load(1)
            cls._latch_load(0)
            
            if (cls._button_sense[0]() == 0 ):  # buttons are inverted
                buttons.append(i*3+1)
            
            if (cls._button_sense[1]() == 0):
                buttons.append(i*3+2)
            
            button_scan = button_scan<<1   ## next scan
        
        return buttons

    async def key(self,b):
        """
        Method to handle key press events. Always overridden

        This method prints the list of pressed keys.

        Args:
            b (list): The list of pressed keys.
        """
        
        print(f"Keyboardio: {b}")
