import dma_defs
import pin_defs
import codec
import math
import struct
import time
import array
import rp2
import machine
from uctypes import addressof


## Set up sample memory arrays

_DEBUG = const(False)

class Waveform(): 
    def __init__(self, num_samples_per_frame=256):
        
        self.outBuffer_ready = False ## flag raised when a sample gets stored and the outBuffers can be written to
                                     ## your code needs to clear this from outside, then wait for next True to sync up
                                     ## at 30 kHz it's about every 38 ms.
        self.num_samples = num_samples_per_frame
        self.outBufferX = bytearray(self.num_samples * 2) ## 2 bytes, 1 channel
        self.outBufferY = bytearray(self.num_samples * 2)
        self.outBuffer = bytearray(self.num_samples * 4)  ## interleave
        self.outBuffer_addr = array.array("L", [addressof(self.outBuffer)]) 
        
        ## This DMA takes the whole block of samples and feeds them off to
        ##  the codec's write PIO state machine
        ## It fires off an IRQ (feed_dac_irq_handler) when it's done with a round
        ## feed_dac_irq_handler interleaves the two sample channels and queues them up
        self.feed_dac_transfer = rp2.DMA()
        ## And this DMA is chained to the above, resets it back to the beginning
        self.feed_dac_control  = rp2.DMA()
        ## Control defs:
        ##  {'inc_read': 0, 'high_pri': 0,  'ring_sel': 0, 'size': 0, 
        ##   'enable': 0, 'treq_sel': 0, 'sniff_en': 0,  'chain_to': 0, 
        ##   'inc_write': 0, 'ring_size': 0, 'bswap': 0, 'IRQ_quiet': 0}
        self.feed_dac_transfer.ctrl = self.feed_dac_transfer.pack_ctrl(default = 0, 
                                                            size      = dma_defs.SIZE_4BYTES,
                                                            enable    = 1,
                                                            treq_sel  = dma_defs.DREQ_PIO0_TX1,
                                                            chain_to  = self.feed_dac_control.channel_id,
                                                            bswap     = 1,
                                                            IRQ_quiet = 0, 
                                                            inc_read  = 1) 
        self.feed_dac_transfer.config(count = self.num_samples, write = codec.WRITE_FIFO)  
        self.feed_dac_transfer.irq(handler=self.feed_dac_irq_handler, hard=False)

        self.feed_dac_control.ctrl = self.feed_dac_control.pack_ctrl(default = 0, 
                                                            size      = dma_defs.SIZE_4BYTES,             ## addresses
                                                            enable    = 1,
                                                            chain_to  = self.feed_dac_control.channel_id, ## no chain
                                                            treq_sel  = dma_defs.TREQ_PERMANENT,          ## always on
                                                            IRQ_quiet = 1)
        self.feed_dac_control.config(count   = 1,
                                     write   = self.feed_dac_transfer.registers[15:],
                                     read    = addressof(self.outBuffer_addr),
                                     trigger = True)
        if _DEBUG: 
            self.debug_pin = machine.Pin(28, machine.Pin.OUT, value=0)
            
    def init(self):
        self.__init__()

    def deinit(self):
        """unwind all of the above"""
        print("(@_@) TODO: verify DMA shuts down")
        self.feed_dac_control.ctrl = 0
        time.sleep_ms(10)  ## (@_@) replace with asyncio when necessary
        self.feed_dac_transfer.ctrl = 0
        self.feed_dac_control.close()
        time.sleep_ms(10)  ## (@_@) replace with asyncio when necessary
        self.feed_dac_transfer.close()
        
    ## 175 us?  not horrible -- roughly 6 sample frames, have 256 
    @micropython.viper
    def interleave_buffers(self):
        bufX_p = ptr16(self.outBufferX)
        bufY_p = ptr16(self.outBufferY)
        out_buffer_p = ptr32(self.outBuffer)
        num_samples = int(self.num_samples)
        for i in range(num_samples):
            out_buffer_p[i] = (bufY_p[i] << 16) +  bufX_p[i] 

    @micropython.viper 
    def feed_dac_irq_handler(self, calling_dma):
        ## this is where the magic happens
        ## roughly every 8.5 ms @ 256 samples
        if _DEBUG:
            self.debug_pin.high()
        self.interleave_buffers()
        self.outBuffer_ready = True
        ## Ping the user to load up their data
        if _DEBUG:
            self.debug_pin.low()

    ## Get data into the buffers
    @micropython.viper
    def _constant(self, value:int, buffer):
        buffer_p = ptr8(buffer)
        num_samples = int(self.num_samples)
        for i in range(num_samples):
            buffer_p[2*i+0] = (value & 0xFF00) >> 8 
            buffer_p[2*i+1] = value & 0x00FF

    @micropython.viper
    def _pack_wave(self, wavelist, buffer):
        """takes a list of integers, +/- 15 bits worth, and packs it into a buffer"""
        buffer_p = ptr8(buffer)
        num_samples = int(self.num_samples)
        for i in range(num_samples):
            sample = int(wavelist[i])
            buffer_p[2*i+0] = (sample & 0xFF00) >> 8 
            buffer_p[2*i+1] = sample & 0x00FF

    ## Convenience functions
    def packX(self, wavelist):
        self._pack_wave(wavelist, self.outBufferX)
    def packY(self, wavelist):
        self._pack_wave(wavelist, self.outBufferY)
    def constantX(self, value:int):
        self._constant(value, self.outBufferX)
    def constantY(self, value:int):
        self._constant(value, self.outBufferY)
    def point(self, x:int, y:int):
        self._constant(x, self.outBufferX)
        self._constant(y, self.outBufferY)



