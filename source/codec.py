from machine import Pin, SPI, PWM, I2C, I2S, PWM, freq
import time
import rp2
import machine
import pin_defs
import pio_defs
import pio_code

## I2C bus address
ak4619_addr = const(0x10)
READ_FIFO    = pio_defs.PIO0_BASE + pio_defs.RXF0_OFFSET ## 0, 0
WRITE_FIFO   = pio_defs.PIO0_BASE + pio_defs.TXF1_OFFSET ## 0, 1

class Codec():
    def __init__(self):
        # RPi I2S doesn't have master clock -- we make one with PWM
        # 125000000 / 16  = 7.8125 MHz master clock
        # 250_000_000 / 16 = 7.8125 MHz master clock
        self.MASTER_CLOCK_HZ   = freq() // 32 
        # fs sample clock = MCLK / 256 = 30517.578 Hz
        self.mclk              = Pin(pin_defs.mclk, Pin.OUT)
        self.mclk_pwm          = PWM(self.mclk, freq=self.MASTER_CLOCK_HZ, duty_u16=32768)

        self.bit_clock = Pin(pin_defs.bit_clock, Pin.OUT, value=0) ## fs / 32
        self.lr_clock  = Pin(pin_defs.lr_clock, Pin.OUT, value=0)  ## fs
        self.sd_in     = Pin(pin_defs.sd_in, Pin.IN)               ## In 3/4 (Y=L, X=R)
        self.sd_out    = Pin(pin_defs.sd_out, Pin.OUT, value=0)    ## Out 1/2 (Y=L, X=R)
        self.pdn       = Pin(pin_defs.pdn, Pin.OUT, value=0)       ## Power down on low
        
        self.i2s_read_sm  = rp2.StateMachine(0, pio_code.i2s_read_pio,  freq=self.MASTER_CLOCK_HZ // 2, sideset_base=self.bit_clock, in_base=self.sd_in)
        self.i2s_write_sm = rp2.StateMachine(1, pio_code.i2s_write_pio, freq=self.MASTER_CLOCK_HZ // 2, out_base=self.sd_out)
        self.start()
        
    def deinit(self):
        self.i2s_read_sm.active(0)
        self.i2s_write_sm.active(0)
        self.mclk_pwm.deinit()
        self.pdn.value(0)

    ## Manually resync the PIO state machines so they run in cycle
    def start(self):
        self.mclk_pwm          = PWM(self.mclk, freq=self.MASTER_CLOCK_HZ, duty_u16=32768)
        machine.mem32[pio_defs.PIO0_BASE] = (0b1111 << pio_defs.CLKDIV_RESTART_BIT) ## reset all clock dividers
        machine.mem32[pio_defs.PIO0_BASE] = (0b1111 << pio_defs.SM_ENABLE_BIT)      ## enable all simultaneously to sync up
        self.config_i2c()

    def config_i2c(self):
        self.i2c = I2C(0, scl=Pin(pin_defs.i2c_scl), sda=Pin(pin_defs.i2c_sda), freq=400_000)
        ## Initialize AK4619 registers
        ## PDN starts 0, when goes high, enters config mode after 10 ms -- datasheet
        self.pdn.value(1)      
        time.sleep_ms(10)         
        ## Config for 16-bit samples & 16-bit slots
        self.i2c.writeto(ak4619_addr, bytes([0x01, 0x3A])) # MSB Justified, 16 bit slot and read data on falling bit-clock
        self.i2c.writeto(ak4619_addr, bytes([0x02, 0x0A])) # 16 bit data on in and out
        ## Config single-ended input on 3 & 4
        self.i2c.writeto(ak4619_addr, bytes([0x0B, 0x05])) 
        ## slow ADC filters -- need to look into this later?
        self.i2c.writeto(ak4619_addr, bytes([0x0A, 0x22])) 
        self.i2c.writeto(ak4619_addr, bytes([0x0D, 0x06])) 
        self.i2c.writeto(ak4619_addr, bytes([0x00, 0x37])) ## Power on, release reset bit



