from keyboardcb import KeyboardCB

class KeyboardRepeat(KeyboardCB):
    """
    A class that inherits from KeyboardCB and adds functionality to handle key repeat events.

    Attributes:
        repeat_count (int): The number of times a key needs to be pressed before it is considered a repeat.
        key_count (dict): A dictionary that keeps track of the number of times each key has been pressed.
    """
    
    def __init__(self, repeat_count=3, callback={}, filter=[], attach=True):
        """
        The constructor for KeyboardRepeat class.

        Args:
            repeat_count (int): The number of times a key needs to be pressed before it is considered a repeat. Default is 3.
            callback (dict): A dictionary of callback functions. Default is an empty dictionary.
            filter (list): A list of keys to filter. Default is an empty list.
            attach (bool): A flag to indicate if the keyboard should be attached during initialization. Default is True.
        """
        
        super().__init__(callback, filter, False, attach)
        self.key_count = {}
        self.repeat_count = repeat_count

    async def key(self, b):
        """
        Method to handle key press events.

        This method overrides the key method in the parent class. It updates the count of key presses for each key 
        and calls the parent class's key method with the keys that are considered repeats.

        Args:
            b (list): The list of pressed keys.
        """
        
        for item in b:
            if item in self.key_count:
                self.key_count[item] += 1
            else:
                self.key_count[item] = 0  # mark first time
        
        remove = [k for k in self.key_count if k not in b]
        
        for k in remove:
            del self.key_count[k]
        
        superkey = [k for k, v in self.key_count.items() if v == self.repeat_count or v == 0]
        resetkey = [k for k, v in self.key_count.items() if v == self.repeat_count]
        
        for item in resetkey:
            self.key_count[item] = 1    # reset repeat count
        
        await super().key(superkey)
