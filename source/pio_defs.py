

PIO0_BASE = const(0x50200000)
PIO1_BASE = const(0x50300000)

CLKDIV_RESTART_BIT = const(8)
SM_ENABLE_BIT      = const(0) 

FSTAT_OFFSET  = const(0x004)
FDEBUG_OFFSET = const(0x008)

TXF0_OFFSET   = const(0x010)
TXF1_OFFSET   = const(0x014)
TXF2_OFFSET   = const(0x018)
TXF3_OFFSET   = const(0x01C)

RXF0_OFFSET   = const(0x020)
RXF1_OFFSET   = const(0x024)
RXF2_OFFSET   = const(0x028)
RXF3_OFFSET   = const(0x02C)

## Direct write-only access to instruction memory.
INSTR_MEM0 = const(0x048)
INSTR_MEM1 = const(0x04C)
# etc.
INSTR_MEM31 = const(0x0C4)

SM0_CLKDIV = const(0x0C8)
SM1_CLKDIV = const(0x0E0)
SM2_CLKDIV = const(0x0F8)
SM3_CLKDIV = const(0x110)
## Frequency = clock freq / (CLKDIV_INT + CLKDIV_FRAC / 256)







