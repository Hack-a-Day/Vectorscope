"""
Object and functions for GC9A01 screen

MicroPython module: https://github.com/russhughes/gc9a01_mpy
"""
from _typeshed import Incomplete, Incomplete as Incomplete
from typing import Any, List, Optional, Tuple, Union
from machine import Pin, SPI

FAST: int
SLOW: int

BLACK: int
BLUE: int
RED: int
GREEN: int
CYAN: int
MAGENTA: int
YELLOW: int
WHITE: int

class GC9A01:
    def __init__(self, spi: SPI, width: int, height: int, reset: Optional[Pin] = None, dc: Optional[Pin] = None, cs: Optional[Pin] = None, backlight: Optional[Pin] = None, rotation: Optional[int] = 0, buffer_size: Optional[int] = 0) -> None:
        """
        Create a new `GC9A01` object

        required args:
        - `spi` spi device
        - `width` display width
        - `height` display height

        optional args:
        - `reset` reset pin
        - `dc` dc pin
        - `cs` cs pin
        - `backlight` backlight pin
        - `rotation` Orientation of display.
        - `buffer_size` 0 = buffer dynamically allocated and freed as needed.

        Rotation | Orientation
        -------- | --------------------
        0        | 0 degrees
        1        | 90 degrees
        2        | 180 degrees
        3        | 270 degrees
        4        | 0 degrees mirrored
        5        | 90 degrees mirrored
        6        | 180 degrees mirrored
        7        | 270 degrees mirrored
        
        If buffer_size is specified it must be large enough to contain the largest bitmap, font character and/or JPG used (Rows * Columns *2 bytes). Specifying a buffer_size reserves memory for use by the driver otherwise memory required is allocated and free dynamicly as it is needed. Dynamic allocation can cause heap fragmentation so garbage collection (GC) should be enabled.
        """
        ...
    def init(self) -> None:
        """
        Send initialization to the display.
        """
        ...
    def on(self) -> None:
        """
        Turn on the backlight pin if one was defined during init.
        """
        ...
    def off(self) -> None:
        """
        Turn off the backlight pin if one was defined during init.
        """
        ...
    def pixel(self, x: int, y: int, color: int) -> None:
        """
        Set the specified pixel to the given `color`.
        """
        ...
    def line(self, x0: int, y0: int, x1: int, y1: int, color: int) -> None:
        """
        Draws a single line with the provided `color` from (`x0`, `y0`) to (`x1`, `y1`).
        """
        ...
    def hline(self, x: int, y: int, length: int, color: int) -> None:
        """
        Draws a single horizontal line with the provided `color` and `length` in pixels. Along with `vline`, this is a fast version with reduced number of SPI calls.
        """
        ...
    def vline(self, x: int, y: int, length: int, color: int) -> None:
        """
        Draws a single horizontal line with the provided `color` and `length` in pixels.
        """
        ...
    def rect(self, x: int, y: int, width: int, height: int, color: int) -> None:
        """
        Draws a rectangle from (`x`, `y`) with corresponding dimensions
        """
        ...
    def fill_rect(self, x: int, y: int, width: int, height: int, color: int) -> None:
        """
        Fill a rectangle starting from (`x`, `y`) coordinates
        """
        ...
    def blit_buffer(self, *buffer, x: int, y: int, width: int, height: int) -> None:
        """
        Copy bytes() or bytearray() content to the screen internal memory. Note: every color requires 2 bytes in the array
        """
        ...
    def text(self, font, s: int, x: int, y: int, fg: Optional[int] = None, bg: Optional[int] = None) -> None:
        """
        Write text to the display using the specified bitmap font with the coordinates as the upper-left corner of the text. The foreground and background colors of the text can be set by the optional arguments fg and bg, otherwise the foreground color defaults to `WHITE` and the background color defaults to `BLACK`. See the `README.md` in the `fonts/bitmap` directory for example fonts.
        """
        ...
    def write(self, bitap_font, s: int, x: int, y: int, fg: Optional[int] = None, bg: Optional[int] = None) -> None:
        """
        Write text to the display using the specified proportional or Monospace bitmap font module with the coordinates as the upper-left corner of the text. The foreground and background colors of the text can be set by the optional arguments fg and bg, otherwise the foreground color defaults to `WHITE` and the background color defaults to `BLACK`. See the `README.md` in the `truetype/fonts` directory for example fonts. Returns the width of the string as printed in pixels.

        The `font2bitmap` utility creates compatible 1 bit per pixel bitmap modules from Proportional or Monospaced True Type fonts. The character size, foreground, background colors and the characters to include in the bitmap module may be specified as parameters. Use the -h option for details. If you specify a buffer_size during the display initialization it must be large enough to hold the widest character (HEIGHT * MAX_WIDTH * 2).
        """
        ...
    def write_len(self, bitap_font, s) -> int:
        """
        Returns the width of the string in pixels if printed in the specified font.
        """
        ...
    def draw(self, vector_font, s: str, x: int, y: int, color: int, scale: Optional[float] = 1.0) -> None:
        """
        Draw text to the display using the specified hershey vector font with the coordinates as the lower-left corner of the text. The color of the text is controlled by color and the optional argument scale, can be used to make the font larger or smaller. See the `README.md` in the `vector/fonts` directory for example fonts and the utils directory for a font conversion program.
        """
        ...
    def jpg(self, jpg_filename: str, x: int, y:int, method: Optional[int] = FAST) -> None:
        """
        Draw JPG file on the display at the given x and y coordinates as the upper left corner of the image. There memory required to decode and display a JPG can be considerable as a full screen 320x240 JPG would require at least 3100 bytes for the working area + 320x240x2 bytes of ram to buffer the image. Jpg images that would require a buffer larger than available memory can be drawn by passing `SLOW` for method. The `SLOW` method will draw the image a piece at a time using the Minimum Coded Unit (MCU, typically 8x8) of the image.
        """
        ...
    def bitmap(self, bitmap, x: int , y: int, index: Optional[int] = 0) -> None:
        """
        Draw bitmap using the specified x, y coordinates as the upper-left corner of the of the bitmap. The optional index parameter provides a method to select from multiple bitmaps contained a bitmap module. The index is used to calculate the offset to the beginning of the desired bitmap using the modules HEIGHT, WIDTH and BPP values.

        The `imgtobitmap.py` utility creates compatible 1 to 8 bit per pixel bitmap modules from image files using the Pillow Python Imaging Library.

        The `monofont2bitmap.py` utility creates compatible 1 to 8 bit per pixel bitmap modules from Monospaced True Type fonts. See the `inconsolata_16.py`, `inconsolata_32.py` and `inconsolata_64.py` files in the `examples/lib` folder for sample modules and the `mono_font.py` program for an example using the generated modules.

        The character sizes, bit per pixel, foreground, background colors and the characters to include in the bitmap module may be specified as parameters. Use the -h option for details. Bits per pixel settings larger than one may be used to create antialiased characters at the expense of memory use. If you specify a buffer_size during the display initialization it must be large enough to hold the one character (HEIGHT * WIDTH * 2).
        """
        ...
    def pbitmap(self, bitmap, x: int , y: int, index: Optional[int] = 0) -> None:
        """
        Progressive version of `bitmap` that draws the bitmap one line at a time allowing you to draw a bitmap that is larger than available memory.
        """
        ...
    def width(self) -> int:
        """
        Returns the current logical width of the display. (ie a 135x240 display rotated 90 degrees is 240 pixels wide)
        """
        ...
    def height(self) -> int:
        """
        Returns the current logical height of the display. (ie a 135x240 display rotated 90 degrees is 135 pixels high)
        """
        ...
    def rotation(self, r: int) -> None:
        """
        Set the rotates the logical display in a clockwise direction. 0-Portrait (0 degrees), 1-Landscape (90 degrees), 2-Inverse Portrait (180 degrees), 3-Inverse Landscape (270 degrees)

        Rotation | Orientation
        -------- | --------------------
        0        | 0 degrees
        1        | 90 degrees
        2        | 180 degrees
        3        | 270 degrees
        4        | 0 degrees mirrored
        5        | 90 degrees mirrored
        6        | 180 degrees mirrored
        7        | 270 degrees mirrored
        """
        ...

def color565(r: int, g: int, b: int) -> int:
    """
    Pack a color into 2-bytes rgb565 format
    """
    ...

def map_bitarray_to_rgb565(bitarray, buffer, width: int, color: Optional[int] = WHITE, bg_color: Optional[int] = BLACK) -> None:
    """
    Convert a bitarray to the rgb565 color buffer which is suitable for blitting. Bit 1 in bitarray is a pixel with `color` and 0 - with `bg_color`.

    This is a helper with a good performance to print text with a high resolution font. You can use an awesome tool https://github.com/peterhinch/micropython-font-to-py to generate a bitmap fonts from .ttf and use them as a frozen bytecode from the ROM memory.
    """
    ...