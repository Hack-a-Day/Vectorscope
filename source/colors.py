from gc9a01 import color565
import gc9a01 as lcd
import phosphor_gradient_14 

PHOSPHOR = phosphor_gradient_14.phosphor_gradient 

PHOSPHOR_BRIGHT=PHOSPHOR[15]
PHOSPHOR_DARK=PHOSPHOR[12]
PHOSPHOR_BG=PHOSPHOR[0]

BLACK=lcd.BLACK
WHITE=lcd.WHITE
RED=lcd.RED
GREEN=lcd.GREEN
BLUE=lcd.BLUE
CYAN=lcd.CYAN
MAGENTA=lcd.MAGENTA
YELLOW=lcd.YELLOW

GRAY=color565(0x80,0x80,0x80)

def rgb(r,g,b):
    return color565(r,g,b)

