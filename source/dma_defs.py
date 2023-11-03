import machine
from uctypes import BF_POS, BF_LEN, UINT32, BFUINT32, struct, addressof

## configure DMA
BASE          = const(0x50000000)
CHAN_WIDTH    = const(0x40)
CHAN_COUNT    = const(12)

def dma_num_tempy(x):
    return BASE + CHAN_WIDTH * x
## ex: dma_num(7)

def hexmem(x):
    return hex(machine.mem32[x])

def hexaddr(x):
    return hex(addressof(x))

def print_friendly(u32):
    a = (u32 & 0xFF000000) >> 24
    b = (u32 & 0x00FF0000) >> 16
    c = (u32 & 0x0000FF00) >>  8 
    d = (u32 & 0x000000FF)
    print(f'{a:#010b} {b:#010b} {c:#010b} {d:#010b}') 

def dma_scan():
    used = []
    for i in range(12):
        ctrl_reg_contents = machine.mem32[dma_num_tempy(i)+0x10]
        if ctrl_reg_contents != 0:
            used.append(i)
        print(f"{i:02}: {ctrl_reg_contents:#034b}")
    print(f"Used DMAs: {used}")

def dma_debug(dma):
    base=addressof(dma.registers)
    print(f"READ: {dma.registers[0]:x}   WRITE: {dma.registers[1]:x}  COUNT next: {machine.mem32[base+0x804]}  current: {machine.mem32[base+0x08]}")
    print(dma.unpack_ctrl(dma.ctrl))
    print("\n")


## Control fields, packed into a nice structure
##  cribbed from rp2040_pio_dma.py
## Thanks to https://github.com/benevpi/MicroPython_PIO_Music_DMA/blob/main/rp2040_pio_dma.py
DMA_CTRL_FIELDS = {
    "AHB_ERROR":   31<<BF_POS | 1<<BF_LEN | BFUINT32,
    "READ_ERROR":  30<<BF_POS | 1<<BF_LEN | BFUINT32,
    "WRITE_ERROR": 29<<BF_POS | 1<<BF_LEN | BFUINT32,
    "BUSY":        24<<BF_POS | 1<<BF_LEN | BFUINT32,
    "SNIFF_EN":    23<<BF_POS | 1<<BF_LEN | BFUINT32,
    "BSWAP":       22<<BF_POS | 1<<BF_LEN | BFUINT32,
    "IRQ_QUIET":   21<<BF_POS | 1<<BF_LEN | BFUINT32,
    "TREQ_SEL":    15<<BF_POS | 6<<BF_LEN | BFUINT32,
    "CHAIN_TO":    11<<BF_POS | 4<<BF_LEN | BFUINT32,
    "RING_SEL":    10<<BF_POS | 1<<BF_LEN | BFUINT32,
    "RING_SIZE":    6<<BF_POS | 4<<BF_LEN | BFUINT32,
    "INCR_WRITE":   5<<BF_POS | 1<<BF_LEN | BFUINT32,
    "INCR_READ":    4<<BF_POS | 1<<BF_LEN | BFUINT32,
    "DATA_SIZE":    2<<BF_POS | 2<<BF_LEN | BFUINT32,
    "HIGH_PRIORITY":1<<BF_POS | 1<<BF_LEN | BFUINT32,
    "EN":           0<<BF_POS | 1<<BF_LEN | BFUINT32
}

## Control register bit positions
## Configuring DMA is essentially a matter of going through this list, making a choice for each bit, and then writing the result to the CTRL register
BUSY_BIT          = const(24) ## flag, readme
SNIFF_ENABLE_BIT  = const(23) ## flag
BYTE_SWAP_BIT     = const(22) ## flag
IRQ_QUIET_BIT     = const(21) ## flag to quiet IRQ
TREQ_SEL_BIT      = const(15) ## request source
CHAIN_TO_BIT      = const(11) ## chain dest
RING_RW_SEL_BIT   = const(10) ## ring on read (0) or write (1) 
RING_SIZE_BIT     = const(6)  ## if ring, how many bytes: 2**n
INC_WRITE_BIT     = const(5)  ## flag
INC_READ_BIT      = const(4)  ## flag
DATA_SIZE_BIT     = const(2)  ## 2**n bytes (1, 2, 4)
HIGH_PRIORITY_BIT = const(1)  ## scheduling priority
ENABLE_BIT        = const(0)  ## will it run

## For use with DATA_SIZE_BIT
SIZE_1BYTE  = const(0x0)
SIZE_2BYTES = const(0x1)
SIZE_4BYTES = const(0x2)

## DMA Config register offsets
##  
## The aliases are very rich.
## You can always write to one of these 4 and it will _never_ trigger
READ_ADDR   = const(0x00)
WRITE_ADDR  = const(0x04)
TRANS_COUNT = const(0x08)
CTRL        = const(0x10)

## Writing to one of these will _always_ trigger
READ_ADDR_TRIG   = const(0x3C)
WRITE_ADDR_TRIG  = const(0x2C)
TRANS_COUNT_TRIG = const(0x1C)
CTRL_TRIG        = const(0x0C)

## And here are the aliases listed out in order for when you need
##  to configure more than 1 byte in a row
READ_ADDR_0   = const(0x00)
WRITE_ADDR_0  = const(0x04)
TRANS_COUNT_0 = const(0x08)
CTRL_0        = const(0x0C)

CTRL_1        = const(0x10)
READ_ADDR_1   = const(0x14)
WRITE_ADDR_1  = const(0x18)
TRANS_COUNT_1 = const(0x1C)

CTRL_2        = const(0x20)
TRANS_COUNT_2 = const(0x24)
READ_ADDR_2   = const(0x28)
WRITE_ADDR_2  = const(0x2C)

CTRL_3        = const(0x30)
WRITE_ADDR_3  = const(0x34)
TRANS_COUNT_3 = const(0x38)
READ_ADDR_3   = const(0x3C)


## List of all Data Request and Trigger Requests
DREQ_PIO0_TX0   = const(0x00)
DREQ_PIO0_TX1   = const(0x01)
DREQ_PIO0_TX2   = const(0x02)
DREQ_PIO0_TX3   = const(0x03)
DREQ_PIO0_RX0   = const(0x04)
DREQ_PIO0_RX1   = const(0x05)
DREQ_PIO0_RX2   = const(0x06)
DREQ_PIO0_RX3   = const(0x07)
DREQ_PIO1_TX0   = const(0x08)
DREQ_PIO1_TX1   = const(0x09)
DREQ_PIO1_TX2   = const(0x0A)
DREQ_PIO1_TX3   = const(0x0B)
DREQ_PIO1_RX0   = const(0x0C)
DREQ_PIO1_RX1   = const(0x0D)
DREQ_PIO1_RX2   = const(0x0E)
DREQ_PIO1_RX3   = const(0x0F)
DREQ_SPI0_TX    = const(0x10)
DREQ_SPI0_RX    = const(0x11)
DREQ_SPI1_TX    = const(0x12)
DREQ_SPI1_RX    = const(0x13)
DREQ_UART0_TX   = const(0x14)
DREQ_UART0_RX   = const(0x15)
DREQ_UART1_TX   = const(0x16)
DREQ_UART1_RX   = const(0x17)
DREQ_PWM_WRAP0  = const(0x18)
DREQ_PWM_WRAP1  = const(0x19)
DREQ_PWM_WRAP2  = const(0x1A)
DREQ_PWM_WRAP3  = const(0x1B)
DREQ_PWM_WRAP4  = const(0x1C)
DREQ_PWM_WRAP5  = const(0x1D)
DREQ_PWM_WRAP6  = const(0x1E)
DREQ_PWM_WRAP7  = const(0x1F)
DREQ_I2C0_TX    = const(0x20)
DREQ_I2C0_RX    = const(0x21)
DREQ_I2C1_TX    = const(0x22)
DREQ_I2C1_RX    = const(0x23)
DREQ_ADC        = const(0x24)
DREQ_XIP_STREAM = const(0x25)
DREQ_XIP_SSITX  = const(0x26)
DREQ_XIP_SSIRX  = const(0x27)
TREQ_TMR0       = const(0x3B)
TREQ_TMR1       = const(0x3C)
TREQ_TMR2       = const(0x3D)
TREQ_TMR3       = const(0x3E)
TREQ_PERMANENT  = const(0x3F)



