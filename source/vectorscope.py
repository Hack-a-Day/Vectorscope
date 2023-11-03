import gc
import time
import gc9a01
import uctypes
import machine
import _thread

## Badge-specific classes 
from codec import Codec
from screen import Screen
from waveform import Waveform
from adc_reader import ADC_Reader
from pixel_pusher import Pixel_Pusher

## Misc helpers and defines
import dma_defs
import pin_defs

class Vectorscope():

    def __init__(self, screen_running = False):
       
        ## Couple buttons if you want to play with them
        # self.audio_shutdown_pin = machine.Pin(pin_defs.audio_shutdown, machine.Pin.OUT, value=1)
        self.user_button        = machine.Pin(pin_defs.user_button, machine.Pin.IN)
        
        ## Turn up the heat!
        machine.freq(250_000_000)
        
        if not screen_running:
            ## We actually only use the raster screen for the init routine.  
            ## So don't need to re-init if coming from the main menu
            self.screen = Screen()
            self.screen.tft.fill(gc9a01.BLACK)
            ## deinit here since we don't need screen around 
            self.screen.deinit()
            gc.collect()

        ## start up I2S state machines
        self.codec = Codec()
        gc.collect()

        ## Fire up the I2S output feeder
        self.wave = Waveform() 
        gc.collect()

        ## sets up memory, DMAs to continuously read in ADC data into a 16-stage buffer
        self.adc_reader = ADC_Reader()
        gc.collect()

        ## automatically blits memory out to screen
        ## needs adc_reader b/c needs to know where samples go
        ## this is the real house of cards...
        self.pixel_pusher = Pixel_Pusher(self.adc_reader)
        gc.collect()

        ## start up the phosphor effect feeder on the other core, 
        ##  b/c it's a ridiculous CPU hog with precise timing requirements
        self.kill_phosphor = False
        _thread.start_new_thread(self.phosphor, [()])


    
    def phosphor(self, thread_callback_stuff):
        previous_frame = self.adc_reader.current_frame
        ## end of frame counter for pixel pusher, used to trigger next frame 
        end_of_pixel_counter = uctypes.addressof(self.pixel_pusher.frame_counter_lookup)+1024*4 
        while not self.kill_phosphor:
            ## wait for ADC frame change to sync up
            while self.adc_reader.current_frame == previous_frame:
                pass     ## (@_@) this could be an async wait: should have ~10 ms of CPU time 
            previous_frame = self.adc_reader.current_frame

            ## While reading this ADC frame, push out all the others to the screen
            ## starting with the oldest frame,
            ##  i.e. the next one in line.  (circular buffer and all that.)
            frame_counter = (self.adc_reader.current_frame + 1) & 0x0F
            phosphor_counter = 1  ## this is the dimmest / off phosphor level
            for i in range(15):
                ## Start off a frame's worth of pixels off to the screen
                self.pixel_pusher.boop(phosphor_counter, (frame_counter+i) & 0x0F)
                ## next brighter color up next
                phosphor_counter = phosphor_counter + 1  
                ## wait for pixel frame to finish -- this is happening in a DMA/PIO chain asynchronously
                while self.pixel_pusher.pixel_frame_counter.read != end_of_pixel_counter: 
                    pass   ## this one should be a busy-wait. 
                           ## It's on the order of microseconds, depending on screen speed. 

            gc.collect()  ## doing this preemptively here where we have time prevents it from happening when we don't want
                          ## One gc.collect per 35 ms is excessive.  But it makes the beast happy, and we're stalling anyway.
        _thread.exit()

    def deinit(self):

        self.kill_phosphor = True
        machine.freq(125_000_000)

        self.pixel_pusher.deinit()
        self.adc_reader.deinit()
        self.wave.deinit()
        self.codec.deinit()

        ## doesn't seem to work.  
        ## Get OS Error 16 on next run
        ## brute force... grrr...
        machine.reset()
        

    def call_out(self):
        pass


