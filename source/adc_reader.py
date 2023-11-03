from uctypes import addressof
import array
import rp2
import time
import machine
import dma_defs
import pio_defs

# read_debug = machine.Pin(26, machine.Pin.OUT)

num_frames            = const(16)
num_samples_per_frame = const(1024)
bytes_per_sample      = const(4)
audio_data_length     = const(num_frames * num_samples_per_frame *  bytes_per_sample)

class ADC_Reader():

    def __init__(self):

        self.num_samples_per_frame = num_samples_per_frame
        ## Setup storage for frames of samples
        self.audio_data = bytearray(audio_data_length)
        ## and the individual frames start here
        self.frame_starts = array.array("L", [addressof(self.audio_data) + i*num_samples_per_frame*bytes_per_sample for i in range(num_frames)])
        self.current_frame = 0
        ## finish up init
        self.align_frame_lookup_address()
        self.config_dmas()

    def init(self):
        self.__init__()

    def deinit(self):
        """unwind all of the above"""
        self.audio_read_control.ctrl = 0
        time.sleep_ms(10)  ## (@_@) replace with asyncio when necessary
        self.audio_read_transfer.ctrl  = 0
        self.audio_read_control.close()
        time.sleep_ms(10)  ## (@_@) replace with asyncio when necessary
        self.audio_read_transfer.close()

    def pause(self):
        self.audio_read_transfer.ctrl &= ~(1)  ## mask enable bit
        time.sleep_ms(10)
        self.audio_read_control.ctrl &= ~(1)  ## mask enable bit

    def resume(self):
        self.audio_read_control.ctrl |= 1  ## set enable bit
        time.sleep_ms(10)
        self.audio_read_transfer.ctrl |= 1 ## set enable bit
        self.audio_read_transfer.config(trigger=True)
 
    @micropython.viper 
    def audio_read_frame_interrupt(self, calling_dma):
        """fires off once per frame, in parallel with audio_read_control"""
        # read_debug.high()
        self.current_frame = (int(self.current_frame)+1) & 0x0F
        ## setup frames/colors and trigger pixel pusher here
        ## want it to go through one cycle -- 15 frames at 15 colors. 

        # read_debug.low()

    def config_dmas(self):
        self.audio_read_transfer = rp2.DMA()
        #print("self.audio_read_transfer")
        #print(self.audio_read_transfer)
        self.audio_read_control  = rp2.DMA()
        #print("self.audio_read_control")
        #print(self.audio_read_control)
        self.audio_read_transfer.ctrl = self.audio_read_transfer.pack_ctrl(default   = 0,
                                                                size      = dma_defs.SIZE_4BYTES,
                                                                enable    = 1,
                                                                treq_sel  = dma_defs.DREQ_PIO0_RX0,
                                                                inc_write = 1,
                                                                chain_to  = self.audio_read_control.channel_id
                                                                )
        self.audio_read_transfer.config(count = num_samples_per_frame,
                                read  = pio_defs.PIO0_BASE + pio_defs.RXF0_OFFSET)
        self.audio_read_transfer.irq(handler = self.audio_read_frame_interrupt)
        # manual trigger
        # self.audio_read_transfer.config(write = audio_data, trigger=True)

        self.audio_read_control.ctrl = self.audio_read_control.pack_ctrl(default   = 0,
                                                            size      = dma_defs.SIZE_4BYTES,
                                                            enable    = 1,
                                                            treq_sel  = dma_defs.TREQ_PERMANENT,
                                                            IRQ_quiet = 1,
                                                            chain_to  = self.audio_read_transfer.channel_id,
                                                            inc_read  = 1,
                                                            ring_size = 6) ## 16 addresses * 4 bytes
        ## feed write addresses of each frame start when done with a frame
        self.audio_read_control.config(write    = addressof(self.audio_read_transfer.registers[1:]),
                                read    = self.frame_lookup_address,
                                count   = 1,
                                trigger = True)


    def align_frame_lookup_address(self):
        ## Need to align this for DMA to enable ring looping over frame starts.
        ## each address is 4 bytes, need 16 of them: 2+4 = 6 bits clear -- align to nearest 0b11000000 = C0
        ## with 64 bytes to be stored, need 128 to guarantee clear  (2x num_frames * 4 bytes)
        ## Make an aligned lookup table for DMA porpoises
        self.frame_lookup = bytearray(num_frames * 4 * 2)
        self.frame_lookup_address = addressof(self.frame_lookup)

        ## spool forward to nearest /64 block : frame_lookup_address is now ready to use
        while self.frame_lookup_address != self.frame_lookup_address & (0xFFFFFFC0):
            self.frame_lookup_address = self.frame_lookup_address + 1

        ## copy frame starts over into lookup LSB first
        ## could probably do this with struct.pack()?
        tempaddress = self.frame_lookup_address
        for f in self.frame_starts:
            machine.mem8[tempaddress] = f & 0xFF
            machine.mem8[tempaddress+1] = (f & 0xFF00) >> 8
            machine.mem8[tempaddress+2] = (f & 0xFF0000) >> 16
            machine.mem8[tempaddress+3] = (f & 0xFF000000) >> 24
            tempaddress = tempaddress + 4


    ####################################
    ##  Residual useful debugging stuff
    ####################################
    
    def debug_print_frames(self,n):
        for j in range(16):
            print(f'############## {j} ################')
            for i in range(n):
                dma_defs.print_friendly(machine.mem32[self.frame_starts[j]+4*i])

    def dma_frame_diagnostics(self):
        current_write_addr    = self.audio_read_transfer.write
        current_frame_pointer = self.audio_read_control.read
        current_frame = (current_frame_pointer - self.frame_lookup_address) // 4
        current_frame_start_addr = machine.mem32[current_frame_pointer]
        print("Address of frame start pointer")
        print(hex(current_frame_pointer))
        print("Address of frame start")
        print(hex(current_frame_start_addr))
        print(f"Frame number: {current_frame}")
        print("Address of current datapoint")
        print(hex(current_write_addr))




