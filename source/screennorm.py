import gc9a01
from machine import Pin, SPI
import vga1_16x32 as font
import gc
import romans as deffont

class ScreenNorm:
    """
    A light wrapper around the gc9a01 screen.

    Attributes:
        _spi (SPI): The SPI interface.
        tft (gc9a01.GC9A01): The TFT display.
    """
    
    def __init__(self):
        """
        The constructor for ScreenNorm class.
        """
        
        self._spi = SPI(0, baudrate=40000000, sck=Pin(2, Pin.OUT), mosi=Pin(3, Pin.OUT), miso=Pin(20,Pin.IN))
        self.wake()

    def get_font(self):
        """
        Get the normal font
        
        Returns:
            font object
        """
        return font
    
    def get_vfont(self):
        """
        Get the default vector font (romans)
        """
        return deffont
    
    def wake(self):
        """
        Method to wake up the display.
        """
        
        self.tft = gc9a01.GC9A01(self._spi, 240, 240,
            reset=Pin(4, Pin.OUT),
            cs=Pin(26, Pin.OUT),  
            dc=Pin(5, Pin.OUT),
            backlight=Pin(27, Pin.OUT),  
            rotation=0)
        
        self.tft.init()

    def idle(self):
        """
        Method to get the display out of the way for another screen helper.
        """
        
        self._spi.deinit()
        self.tft=None

    def jpg(self,filename):
        """
        Method to show a jpg on the display.

        Args:
            filename (str): The name of the jpg file.
        """
        
        if self.tft!=None:
            gc.collect()   
            self.tft.jpg(filename,0,0,1)

    def text(self,x,y,txt,fg_color=gc9a01.color565(45, 217, 80),bg_color=gc9a01.color565(10,15,10)):
        """
        Method to draw text on the display.

        Args:
            x (int): The x-coordinate of the top left corner of the text.
            y (int): The y-coordinate of the top left corner of the text.
            txt (str): The text to draw.
            fg_color (int): The foreground color. Default is gc9a01.color565(243,191,16).
            bg_color (int): The background color. Default is gc9a01.color565(26,26,26).
        """
        
        if self.tft!=None:
            self.tft.text(font,txt,x,y,fg_color,bg_color)

    def text_font(self,font,x,y,txt,fg_color=gc9a01.color565(45, 217, 80),scale=1.0):
        """
        Method to draw text with a font.
        
        Args:
            font (font or None): The font to use (or use default font)
            x,y (int): X and Y coordinate
            txt (str): String
            fg_color (int) Foreground color (note: no background color -- always transparent)
        """
        if self.tft!=None:
            if font==None:
                font=deffont
            self.tft.draw(font,txt,x,y,fg_color,scale)
    
    def clear(self,color=0):
        """
        Method to clear the display with a color.

        Args:
            color (int): The background color. Default is 0.
        """
        
        if self.tft!=None:
            self.tft.fill_rect(0,0,240,240,color)

    def pixel(self,x,y,color):
        """
        Method to set a pixel on the display.

        Args:
            x (int): The x-coordinate of the pixel.
            y (int): The y-coordinate of the pixel.
            color (int): The color of the pixel.
        """
        
        if self.tft!=None:
             self.tft.pixel(x,y,color)
