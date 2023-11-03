import keyleds
import keyboardio
import asyncio

class KeyboardCB(keyboardio.KeyboardIO):
    """
    A class that provides a single callback for a key or group of keys.
    It can use a single callback or a dictionary to have different callbacks for different keys.
    It can also filter repeating keys

    Attributes:
        callback (dict or function): A dictionary of callback functions or a single callback function.
        filter (list): A list of keys to filter (default none, or use keys from callback when callback is a dictionary)
        single_key_mode (bool): A flag to indicate if only single key press events should be handled.
        attach (bool): A flag to indicate if the keyboard should be attached during initialization.
        active (bool): A flag to indicate if the keyboard is active.
    """
    
    def __init__(self, callback={}, filter=[], single_key_mode=True, attach=True):
        """
        The constructor for KeyboardCB class.

        Args:
            callback (dict or function): A dictionary of callback functions or a single callback function.
               Default is an empty dictionary (no callbacks).
            filter (list): A list of keys to filter. Default is an empty list.
            single_key_mode (bool): A flag to indicate if only single key press events should be handled. Default is True.
            attach (bool): A flag to indicate if the keyboard should be attached during initialization. Default is True.
        """
        super().__init__(attach=attach)
        if isinstance(filter,list):
            self.filter=filter
        else:
            self.filter=[ filter ]
        self._cb=callback
        self.single_key_mode=single_key_mode
        self.active=True

    def set_callback(self,func_or_dict):
        """
        Function to set a non-default callback.

        Args:
            func_or_dict (function or dict): The function or dictionary to set as the callback.
        """
        self._cb=func_or_dict

    async def _do_callback(self,cb,k):
        try:
           await cb(k)   # async if possible 
        except TypeError:  # well, it was really a sync call, np...
            pass
        
    async def key(self, b):
        """
        Function to handle key press events.

        This function checks if the keyboard is active and if the pressed key is in the filter. 
        If it is, it calls the appropriate callback function.

        Args:
            b (int): The keycodes of the pressed keys as a list.
        """
        
        # if you specify a filter, use it
        # if not but you use a dictionary callback, use its keys as a filter
        # otherwise, no filter
        if self.active==False:
            return    
        
        if self.filter!=[]:
            flt=self.filter
        else:
            if isinstance(self._cb,dict):
                flt=self._cb.keys()
            else:
                flt=[]
        
        #  remove all not in filter here first
        if flt!=[]:
            b1=[ item for item in b if item in flt ]
        else:
            b1=b
        
        if (b1!=[] and self.single_key_mode==True):    # single keypress mode
            b1=[ item for item in b1 if item not in self._prev ]
        
        if b1:
            for k in b1:
                if flt!=[]:
                    if k not in flt:
                        continue
                
                if isinstance(self._cb,dict):
                    asyncio.create_task(self._do_callback(self._cb[k],k))
                else:
                    asyncio.create_task(self._do_callback(self._cb,k))

def replace_chord(b,chord,value):
    """
    Helper function to find chords (two or more keys) and replace them with one key.

    Args:
       b (list): The list of pressed keys.
       chord (list): The list of keys that form a chord.
       value (int): The keycode of the key that will replace the chord.

    Returns:
       list: The list of pressed keys with the chord replaced by the value.
    """
    
    b1=b
    
    if all(item in b1 for item in chord):
        for item in chord:
            b1.remove(item)
        
        b1.append(value)
    
    return b1

