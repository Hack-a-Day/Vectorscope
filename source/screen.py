from machine import Pin, SPI, SoftSPI
import pin_defs
import gc9a01
import gc
import rp2

class Screen():
    def __init__(self, softSPI=False):
        self.softSPI = softSPI
        self.sck  = Pin(pin_defs.sck, Pin.OUT)
        self.data = Pin(pin_defs.data, Pin.OUT)
        self.dc   = Pin(pin_defs.dc, Pin.OUT)
        self.init()

    def deinit(self):
        self.spi.deinit()
        ## this does not appear to de-initialize the DMAs -- the enable bits are still set
        del(self.spi)
        del(self.tft)
        gc.collect()

    def init(self):
        if self.softSPI:
            self.spi = SoftSPI(baudrate=10_000_000, sck=self.sck, mosi=self.data, miso=Pin(pin_defs.throwaway))
        else:
            self.spi = SPI(0, baudrate=40_000_000, sck=self.sck, mosi=self.data)
        
        self.tft = gc9a01.GC9A01(self.spi, 240, 240,
                            reset     = Pin(pin_defs.reset, Pin.OUT),
                            cs        = Pin(pin_defs.throwaway, Pin.OUT), ## not used, grounded on board
                            dc        = self.dc,
                            backlight = Pin(pin_defs.throwaway, Pin.OUT), ## not used, always on
                            rotation  = 0)
        self.tft.init()   
        self.tft.fill(gc9a01.color565(10,15,10))


if __name__ == "__main__":

    import time
    import random

    ## instantiate and init
    s = Screen()

    ## For everything you can do with the GC9A01 library:
    ## https://github.com/russhughes/gc9a01_mpy

    s.tft.fill(gc9a01.BLUE)
    time.sleep_ms(500)
    s.tft.fill(gc9a01.YELLOW)
    time.sleep_ms(500)
    s.tft.fill(gc9a01.BLACK)

    phosphor_bright = gc9a01.color565(120, 247, 180)
    phosphor_dark   = gc9a01.color565(45, 217, 80)

    ## better graphic demo should go here
    for i in range(200):
        x1 = random.randint(0, 240)
        x2 = random.randint(0, 240)
        y1 = random.randint(0, 240)
        y2 = random.randint(0, 240)

        if i % 2:
            s.tft.line(x1, y1, x2, y2, phosphor_bright)
        else:
            s.tft.line(x1, y1, x2, y2, phosphor_dark)
        time.sleep_ms(20)





