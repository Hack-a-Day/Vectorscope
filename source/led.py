import keyboardio
import keyleds
import asyncio

class LED:
    """
    A class to represent an LED.

    ...

    Attributes
    ----------
    mask : int
        a bitmask representing the LED

    Methods
    -------
    set():
        Sets the LED.
    reset():
        Resets the LED.
    toggle():
        Toggles the LED.
    """

    def __init__(self, mask):
        """
        Constructs all the necessary attributes for the LED object.

        Parameters
        ----------
            mask : int
                a bitmask representing the LED
        """
        self.mask = mask

    def set(self):
        """Sets the LED by applying the mask to the keyboard LEDs."""
        keyboardio.KeyboardIO.leds |= self.mask

    def reset(self):
        """Resets the LED by applying the inverted mask to the keyboard LEDs."""
        keyboardio.KeyboardIO.leds &= ~self.mask

    def toggle(self):
        """Toggles the LED by XORing the mask with the keyboard LEDs."""
        keyboardio.KeyboardIO.leds ^= self.mask
    
    def __call__(self,value):
        self.value=value

    @property
    def value(self):
        """
        Gets the value of the LED.

        Returns
        -------
            bool
                True if the LED is set, False otherwise.
        """
        return (keyboardio.KeyboardIO.leds & self.mask) != 0

    @value.setter
    def value(self, val):
        """
        Sets or resets the LED based on the provided value.

        Parameters
        ----------
            val : bool
                The value to set. If True, the LED is set. If False, it is reset.
        """
        if val:
            self.set()
        else:
            self.reset()

# Create instances of LEDs with different masks.
X = LED(keyleds.LED_X)
Y = LED(keyleds.LED_Y)
Triangle = LED(keyleds.LED_TRI)
Square = LED(keyleds.LED_SQ)
Sine = LED(keyleds.LED_SINE)
Sig = LED(keyleds.LED_SIG)
Scope = LED(keyleds.LED_SCOPE)
Saw = LED(keyleds.LED_SAW)


if __name__=="__main__":
    from vectoros import sleep_forever
    from timer import Timer
    
    keyboardio.KeyboardIO.run(50)
    Timer.run()  
    
    flip=False
    
    def tick():
        global flip
        if flip:
            Y.set()
            X.reset()
            flip=False
            Scope.value=1
            Sig(False)
        else:
            Y.reset()
            X.set()
            flip=True
            Scope.value=0
            Sig(True)
        Sine.toggle()
        
    Timer.add_timer(10,tick)
    sleep_forever()