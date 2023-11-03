from vectorscope import Vectorscope
from dds import DDS

import gc
from vos_debug import debug_print as debug
import vectoros
import vos_state
import vos_debug
import keyboardcb
import keyleds
import keyboardio
import asyncio

_abort=False
## map waveform types to LEDs
_waves_lookup = {0:"sine", 3:"sawtooth", 1:"square", 2:"triangle"}
_waves_reverse_lookup = {"sine":0, "sawtooth":3, "square":1, "triangle":2}

lissajous_state = {
        "selected_axis":0, 
        "selected_waveform":0,
        "waves_leds":[0,0]

        }

async def do_dds_loop(d):
    while not _abort:
        for i in range(50):
            d.do_dds()
            d.populate_buffer()
            await asyncio.sleep(0)
    
def do_abort(key):
    global _abort
    _abort=True


async def vos_main():

    vectoros.get_screen().idle()
    gc.collect()
    vos_state.gc_suspend=True
    # await asyncio.sleep(1)
    
    keyboardio.KeyboardIO.leds = (1<<7) 
    keyboardio.KeyboardIO.leds |= (1<<5) ## sine wave
    keyboardio.KeyboardIO.scan()

    v = Vectorscope()
    d = DDS(v)
    d.increment = [1500, 1200]
    d.amplitude=[0.5, 0.5]
    d.recalculate_waveforms()

    def toggle_xy(key):
        ## not right yet
        global lissajous_state
        global d
        if lissajous_state["selected_axis"] == 0:
            lissajous_state["selected_axis"] = 1
            keyboardio.KeyboardIO.leds |= (1<<6)
            keyboardio.KeyboardIO.leds &= ~(1<<7)
        else:
            lissajous_state["selected_axis"] = 0
            keyboardio.KeyboardIO.leds |= (1<<7)
            keyboardio.KeyboardIO.leds &= ~(1<<6)
        
        ## Update leds to reflect switch
        keyboardio.KeyboardIO.leds &= (0b11000011)
        which_led = lissajous_state["waves_leds"][lissajous_state["selected_axis"]] 
        keyboardio.KeyboardIO.leds |= (1<<(5-which_led))

    def toggle_waveform(key):
        global lissajous_state
        which_led = lissajous_state["waves_leds"][lissajous_state["selected_axis"]] 
        ## clear leds
        keyboardio.KeyboardIO.leds &= (0b11000011)
        ## update led
        which_led = ( which_led + 1) % 4 
        keyboardio.KeyboardIO.leds |= (1<<(5-which_led ))
        ## update storage
        lissajous_state["waves_leds"][lissajous_state["selected_axis"]] = which_led
        ## update waveform
        d.waveform[lissajous_state["selected_axis"]] = _waves_lookup[which_led]
        d.recalculate_waveforms()
        
    def handle_joystick_up(key):
        current_keys = keyboardcb.KeyboardCB.current_keys
        if len(current_keys) == 1: ## just joystick
            d.increment[1] = int(d.increment[1] * 1.1)
        if keyleds.KEY_RANGE in current_keys:
            d.amplitude[1] = d.amplitude[1] * 1.1
            d.recalculate_waveforms()
            ## increase amplitude Y
        if keyleds.KEY_LEVEL in current_keys:
            d.phase_increment[1] = d.phase_increment[1] + 1
            ## increase phase Y
        
    def handle_joystick_down(key):
        current_keys = keyboardcb.KeyboardCB.current_keys
        if len(current_keys) == 1: ## just joystick
            d.increment[1] = int(d.increment[1] * 0.91)
        if keyleds.KEY_RANGE in current_keys:
            d.amplitude[1] = d.amplitude[1] * 0.91
            d.recalculate_waveforms()
            ## increase amplitude Y
        if keyleds.KEY_LEVEL in current_keys:
            d.phase_increment[1] = d.phase_increment[1] - 1
            ## increase phase Y
    def handle_joystick_right(key):
        current_keys = keyboardcb.KeyboardCB.current_keys
        if len(current_keys) == 1: ## just joystick
            d.increment[0] = int(d.increment[0] * 1.1)
        if keyleds.KEY_RANGE in current_keys:
            d.amplitude[0] = d.amplitude[0] * 1.1
            d.recalculate_waveforms()
            ## increase amplitude Y
        if keyleds.KEY_LEVEL in current_keys:
            d.phase_increment[0] = d.phase_increment[0] + 1
            ## increase phase Y
        
    def handle_joystick_left(key):
        current_keys = keyboardcb.KeyboardCB.current_keys
        if len(current_keys) == 1: ## just joystick
            d.increment[0] = int(d.increment[0] * 0.91)
        if keyleds.KEY_RANGE in current_keys:
            d.amplitude[0] = d.amplitude[0] * 0.91
            d.recalculate_waveforms()
            ## increase amplitude X
        if keyleds.KEY_LEVEL in current_keys:
            d.phase_increment[0] = d.phase_increment[0] - 1
            ## increase phase X

    mykeys=keyboardcb.KeyboardCB({keyleds.KEY_MENU: do_abort, 
                                  keyleds.KEY_XY:toggle_xy,
                                  keyleds.KEY_WAVE: toggle_waveform,
                                  keyleds.JOY_UP: handle_joystick_up,
                                  keyleds.JOY_DN: handle_joystick_down,
                                  keyleds.JOY_RT: handle_joystick_right,
                                  keyleds.JOY_LT: handle_joystick_left
                                  })
    await do_dds_loop(d)
    
    vectoros.reset()



