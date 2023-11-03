## pixel pusher!
import rp2
import array
import machine
import pin_defs
import dma_defs
import pio_code
import pio_defs
import micropython
from phosphor_gradient_14 import phosphor_gradient
from uctypes import addressof

## allows interrupts to throw errors
import micropython
micropython.alloc_emergency_exception_buf(100)

NOP       = const(41) # 0x29 -- display on
SET_X     = const(42) # 0x2A -- column select
SET_Y     = const(43) # 0x2B -- row select
SET_COLOR = const(44) # 0x2C -- send data
X_MSB_OFFSET = const(1)  # data from ADC comes 16 bits X | 16 bits Y, LSB order
Y_MSB_OFFSET = const(3)

COLOR_MASK = const(0x0F) ## 16 colors max
FRAME_MASK = const(0x0F) ## 16 colors max

_LOOPING = const(False)
_IRQ     = const(False)
# pixel_debug = machine.Pin(27, machine.Pin.OUT)

class Pixel_Pusher():

    @micropython.viper 
    def boop(self, color:int, frame:int):
        """Trigger me once per adc_reader frame update"""
        # pixel_debug.high()
        ## set frame, color
        machine.mem16[self.color_storage_address] = self.phosphors[color & COLOR_MASK]
        self.stage_sample_data.registers[0] = self.frame_starts[frame & FRAME_MASK]
        ## reset counter lookup
        self.pixel_frame_counter.registers[0] = self.frame_counter_lookup_address  
        ## and go!
        self.stage_sample_data.registers[7] = 1 ## transaction count trigger register
        # pixel_debug.low()

    @micropython.viper 
    def pixel_frame_interrupt_handler(self, dma_caller):
        ## even this is too much  -- my guess is that the IRQs stack up during a GC or other system stupid thing
        self.frame_done = True 

    def resume(self):
        for d in self.allDMAs:
            d.ctrl = d.ctrl | 1
        self.stage_sample_data.config(trigger=True)
    def pause(self):
        for d in self.allDMAs:
            d.ctrl = d.ctrl & ~1  ## clear enable bit
    def deinit(self):
        # print(self.allDMAs)
        self.pixel_pusher_sm.active(0)
        self.pause()
        for d in self.allDMAs:
            d.close()

    def __init__(self, adc_reader):
        ## Consider deinitializing screen here?  Or should that just always happen in code: risky! (@_@)
        ## Needs adc_reader b/c it needs to know where the samples are stored
        self.frame_starts = adc_reader.frame_starts
        self.adc_frame = adc_reader.current_frame
        self.phosphors = phosphor_gradient
        self.num_samples_per_frame = adc_reader.num_samples_per_frame
        self.frame_done = False
        self._init_PIO()
        
        ## Data storage for DMA trickery
        ## These three 32-bit numbers are formatted up to pass to the pixel_pusher_pio 
        ## It takes care of setting the command bit when relevant, and repeating the data
        ## 120s are just placeholders for the X/Y coordinates
        self.pixel_command_array = array.array("B", 
                                               [0, SET_X, 0, 120,
                                                0, SET_Y, 0, 120,
                                                0, SET_COLOR, 0xFF,0xFF,
                                                0, NOP, 0, 0])
        self.pixel_command_addr = array.array("L", [addressof(self.pixel_command_array)]) ## one element, for resetter

        self.command_x     = addressof(self.pixel_command_array) + 3  ## byte position in array
        self.command_y     = addressof(self.pixel_command_array) + 7
        self.command_color = addressof(self.pixel_command_array) + 10

        ## Storage for one sample from ADC  
        self.one_sample_storage = bytearray(4)
        self.one_sample_storage_address = addressof(self.one_sample_storage)
        
        ## Storage for the color
        self.color_storage = bytearray(2)
        ## One way to set it
        machine.mem16[addressof(self.color_storage)] = self.phosphors[15]
        self.color_storage_address = addressof(self.color_storage)

        ## Strange array for counting purposes
        ## returns a count for stage_sample_data, num_samples_per_frame-1 times
        ## and then a 0, which will trigger and IRQ @ end of frame
        ## and then you can reset
        self.frame_counter_lookup = array.array("L", [1]*(self.num_samples_per_frame-1))
        self.frame_counter_lookup.append(0)
        self.frame_counter_lookup_address = addressof(self.frame_counter_lookup)
                
        ## And here's the world's most convoluted DMA / PIO chain!
        self.stage_sample_data       = rp2.DMA() ## pulls one sample pair from memory into bit_flipper_pio
        self.store_flipped_data      = rp2.DMA() ## pulls bit-flipped pair and writes to sample storage 
        self.pixel_load_x            = rp2.DMA() ## extracts X from sample storage, puts it in pixel command array
        self.pixel_load_y            = rp2.DMA() ## extracts Y ...
        self.pixel_load_color        = rp2.DMA() ## extracts color ...
        self.pixel_command_to_screen = rp2.DMA() ## writes pixel command array to screen
        self.pixel_command_resetter  = rp2.DMA() ## resets command_to_screen after three commands
        self.pixel_frame_counter     = rp2.DMA() ## refreshes pixel command array address, stalls stage_sample_data at end of every frame
                                                 ##   by sending a zero read address.  Restart by configuring these two.
        self.allDMAs = [self.stage_sample_data, self.store_flipped_data, self.pixel_load_x , self.pixel_load_y , self.pixel_load_color, self.pixel_command_to_screen,
                        self.pixel_command_resetter , self.pixel_frame_counter ]

        self.pixel_frame_counter_read_address = int(addressof(self.pixel_frame_counter.registers[0:]))

        ## Control defs:
        ##  {'inc_read': 0, 'high_pri': 0,  'ring_sel': 0, 'size': 0, 
        ##   'enable': 0, 'treq_sel': 0, 'sniff_en': 0,  'chain_to': 0, 
        ##   'inc_write': 0, 'ring_size': 0, 'bswap': 0, 'IRQ_quiet': 0}
        self.stage_sample_data.ctrl = self.stage_sample_data.pack_ctrl(default = 0, 
                                                            size      = dma_defs.SIZE_4BYTES,
                                                            enable    = 1,
                                                            treq_sel  = dma_defs.DREQ_PIO0_TX2,  ## pace to TX FIFO
                                                            chain_to  = self.store_flipped_data.channel_id,
                                                            IRQ_quiet = 1, 
                                                            inc_read  = 1
                                                            ) 
        self.stage_sample_data.config(count = 1,
                                      read  = self.frame_starts[0],  ## initial value, set this to start of frame to begin chain
                                      write = pio_defs.PIO0_BASE + pio_defs.TXF2_OFFSET
)
        if _IRQ:
            self.stage_sample_data.irq(handler=self.pixel_frame_interrupt_handler, hard=True)
            ## when one-shot, don't need to interrupt itself.
        

        ## The bit-flipper PIO is in the middle here.
        ## It's  PIO 0, 2

        self.store_flipped_data.ctrl = self.store_flipped_data.pack_ctrl(default = 0,
                                                             size      = dma_defs.SIZE_4BYTES,
                                                             enable    = 1,
                                                             treq_sel  = dma_defs.DREQ_PIO0_RX2,  ## on PIO
                                                             chain_to  = self.pixel_load_x.channel_id,
                                                             IRQ_quiet = 1
                                                             )
        self.store_flipped_data.config(count = 1,
                                       read  = pio_defs.PIO0_BASE + pio_defs.RXF2_OFFSET,
                                       write = self.one_sample_storage_address)
######

        self.pixel_load_x.ctrl = self.pixel_load_x.pack_ctrl(default = 0,
                                                             size      = dma_defs.SIZE_1BYTE,
                                                             enable    = 1,
                                                             treq_sel  = dma_defs.TREQ_PERMANENT,
                                                             chain_to  = self.pixel_load_y.channel_id,
                                                             IRQ_quiet = 1
                                                             )
        self.pixel_load_x.config(count = 1,
                                 read  = self.one_sample_storage_address + X_MSB_OFFSET, 
                                 write = self.command_x)

        self.pixel_load_y.ctrl = self.pixel_load_y.pack_ctrl(default = 0,
                                                             size      = dma_defs.SIZE_1BYTE,
                                                             enable    = 1,
                                                             treq_sel  = dma_defs.TREQ_PERMANENT,
                                                             chain_to  = self.pixel_load_color.channel_id,
                                                             IRQ_quiet = 1
                                                             )
        self.pixel_load_y.config(count = 1,
                                 read  = self.one_sample_storage_address + Y_MSB_OFFSET, 
                                 write = self.command_y)

        self.pixel_load_color.ctrl = self.pixel_load_color.pack_ctrl(default = 0,
                                                             bswap     = 1,
                                                             size      = dma_defs.SIZE_2BYTES,
                                                             enable    = 1,
                                                             treq_sel  = dma_defs.TREQ_PERMANENT,
                                                             chain_to  = self.pixel_command_to_screen.channel_id,
                                                             IRQ_quiet = 1
                                                             )
        self.pixel_load_color.config(count = 1,
                                 read  = self.color_storage_address, 
                                 write = self.command_color)

        self.pixel_command_to_screen.ctrl = self.pixel_command_to_screen.pack_ctrl(default = 0,
                                                                                   bswap     = 1,
                                                                                   inc_read  = 1,
                                                                                   size      = dma_defs.SIZE_4BYTES,
                                                                                   enable    = 1,
                                                                                   treq_sel  = dma_defs.DREQ_PIO1_TX0,
                                                                                   chain_to  = self.pixel_command_resetter.channel_id,
                                                                                   IRQ_quiet = 1,
                                                                                   ring_sel = 0, # ring on read
                                                                                   ring_size = 4  # 2**4 = 16 bytes = 4 transfers
                                                                                   )
        self.pixel_command_to_screen.config(count = 3,
                                            read  = addressof(self.pixel_command_array),   
                                            write = pio_defs.PIO1_BASE + pio_defs.TXF0_OFFSET)  ## PIO sm(4)


        self.pixel_command_resetter.ctrl = self.pixel_command_resetter.pack_ctrl(default   = 0,
                                                                           size      = dma_defs.SIZE_4BYTES,
                                                                           enable    = 1,
                                                                           treq_sel  = dma_defs.TREQ_PERMANENT,
                                                                           IRQ_quiet = 1,
                                                                           chain_to  = self.pixel_frame_counter.channel_id
                                                                           )
        self.pixel_command_resetter.config(count = 1,
                                        write = addressof(self.pixel_command_to_screen.registers[0:]), ##  set read address back to top
                                        read  = addressof(self.pixel_command_addr))

        self.pixel_frame_counter.ctrl = self.pixel_frame_counter.pack_ctrl(default   = 0,
                                                                           inc_read  = 1,
                                                                           size      = dma_defs.SIZE_4BYTES,
                                                                           enable    = 1,
                                                                           treq_sel  = dma_defs.TREQ_PERMANENT,
                                                                           IRQ_quiet = 1,
                                                                           chain_to  = self.pixel_frame_counter.channel_id
                                                                           ## ends the chain.  reset the frame_counter_lookup to restart.
                                                                           )
        self.pixel_frame_counter.config(count = 1,
                                        write = addressof(self.stage_sample_data.registers[7:]), ## count trigger register
                                        read  = addressof(self.frame_counter_lookup))

    
    def _init_PIO(self):
        ## same pins shared with 
        self.sck_pin  = machine.Pin(pin_defs.sck, machine.Pin.OUT)
        self.data_pin = machine.Pin(pin_defs.data, machine.Pin.OUT)
        self.dc_pin   = machine.Pin(pin_defs.dc, machine.Pin.OUT)

        ## PIO 1, 0
        self.pixel_pusher_sm = rp2.StateMachine(4, pio_code.handle_screen_command, freq=250_000_000, 
                                    out_base=self.data_pin, set_base=self.dc_pin, sideset_base=self.sck_pin)
        self.pixel_pusher_sm.active(1)

        ## PIO 0, 2
        self.bit_flipper_sm = rp2.StateMachine(2, pio_code.bit_flipper_pio, freq=250_000_000)
        self.bit_flipper_sm.restart()  ## flush buffers?  belt and suspenders.
        self.bit_flipper_sm.active(1)

