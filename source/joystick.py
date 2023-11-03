import keyleds
import keyboardcb

class Joystick(keyboardcb.KeyboardCB):
    """
    A joystick class that inherits from KeyboardCB. It has a default filter and repeat set.
    It also knows how to replace chords like JOY_N + JOY_E to JOY_NE.

    Attributes:
        callback (dict): A dictionary of callback functions or a single callback.
        single (bool): A flag to indicate if only single key press events should be handled.
        attach (bool): A flag to indicate if the joystick should be attached during initialization.
    """
    
    def __init__(self, callback={}, single_key_mode=False, attach=True):
        """
        The constructor for Joystick class.

        Args:
            callback (dict): A dictionary of callback functions. Default is an empty dictionary.
            single_key_mode (bool): A flag to indicate if only single key press events should be handled. Default is False.
            attach (bool): A flag to indicate if the joystick should be attached during initialization. Default is True.
        """
        super().__init__(callback, keyleds.JOY_ALL, single_key_mode, attach=attach)

    async def key(self, b):
        """
        Function to handle key press events.

        This function generates synthetic keys and dispatches callbacks as usual.

        Args:
            b (int): The keycodes of the pressed keys (list).
        """
        
        # generate synthetic keys
        b1 = keyboardcb.replace_chord(b, [keyleds.JOY_N, keyleds.JOY_E], keyleds.JOY_NE)
        b1 = keyboardcb.replace_chord(b1, [keyleds.JOY_N, keyleds.JOY_W], keyleds.JOY_NW)
        b1 = keyboardcb.replace_chord(b1, [keyleds.JOY_S, keyleds.JOY_E], keyleds.JOY_SE)
        b1 = keyboardcb.replace_chord(b1, [keyleds.JOY_S, keyleds.JOY_W], keyleds.JOY_SW)
        
        await super().key(b1)  # dispatch callbacks as usual
