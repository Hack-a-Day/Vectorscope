import rp2

######################################################
## Define I2S PIO machines  
## 16-bit slots, data
## read on falling edge of bit clock
######################################################

@rp2.asm_pio(sideset_init=[rp2.PIO.OUT_LOW]*2, fifo_join=rp2.PIO.JOIN_RX)
## bitclock and LR clock on the sidesets, respectively 
def i2s_read_pio():
    nop()[3]         ## delay to sync up with write PIO -- empirically determined
    wrap_target()

    set(y,14)        .side(0b00)[1]  ## send 32 bits per LR read
    label("L")
    in_(pins, 1)     .side(0b01)[1]  ## Left, bits
    jmp(y_dec, "L")  .side(0b00)[1]
    in_(pins, 1)     .side(0b11)[1]
   
    set(y,14)        .side(0b10)[1]
    label("R")
    in_(pins,1)      .side(0b11)[1] ## right, bits
    jmp(y_dec, "R")  .side(0b10)[1]
    in_(pins,1)      .side(0b01)

    push(noblock)    ## noblock keeps PIOs in sync
    wrap()

## 10

@rp2.asm_pio(out_init=rp2.PIO.OUT_LOW, fifo_join=rp2.PIO.JOIN_TX)
## runs lockstep with read pio, spits out data when it's got it, zeros otherwise
def i2s_write_pio():
    wrap_target()

    pull(noblock)    ## noblock keeps PIOs in sync
    set(y,14)          ## send 16 bits per LR clock
    label("L")
    out(pins,1)      [1]             ## Left, bits
    jmp(y_dec, "L")  [1]
    out(pins,1)      [1]

    set(y,14)        [1]
    label("R")
    out(pins,1)      [1]
    jmp(y_dec, "R")  [1]
    out(pins,1)      [1]
    wrap()

## 19

@rp2.asm_pio(in_shiftdir=1, out_shiftdir=1) 
def bit_flipper_pio():
    ## takes in two 16-bit as signed/unsigned integers  
    ## converts them by flipping MSBit of each 16-bitter
    ## tailored for reading X/Y channel from DAC and fitting
    ##  the result on the (unsigned 8bit) screen
    pull()
    set(y,1)
    label("twice")
   
    in_(osr, 15) ## copy 15 LSB unchanged to output
    out(null, 15) ## discard 15 bits from OSR to keep pace
    
    mov(osr, invert(osr)) ## inverted what's left
    in_(osr, 1) ## copy out one inverted bit
    out(null, 1) ## drop that bit from OSR 
    mov(osr, invert(osr)) ## reinvert for the next word
    
    jmp(y_dec, "twice")
    push()
    
## 29



########################################################
##  Pixel Pusher: Handle Screen Command
##  Takes commands and data
##   sends it to the screen pretty fast
## Format:
# 0 2A 0 X
# 0 2B 0 Y
# 0 2C C1 C2
##  Screen expects 2A 0 X 0 X 2B 0 Y 0 Y 2C C1 C2  
##   with the commands framed by the DC line going low
##  This PIO ignores the first byte, 
##   transmits the second, framed by DC,
##   then doubles the second pair
##  This means it actually transmits C1 C2 C1 C2, but 
##   the screen doesn't seem to care  (hack, hack!)
########################################################

@rp2.asm_pio(out_init=rp2.PIO.OUT_LOW, set_init=rp2.PIO.OUT_HIGH,
            sideset_init=rp2.PIO.OUT_LOW, autopull=True, autopush=True)
def handle_screen_command():
    pull(block).side(0)
    out(null, 8).side(0) ## drop initial zeros
    
    set(pins, 0).side(0) ## DC set low, CMD mode
   
    set(y,7).side(0)  ## send 8 command bits
    label("send_cmd")
    out(pins, 1).side(0)
    jmp(y_dec, "send_cmd").side(1)

    set(pins, 1).side(0) ## DC set high, data mode

    mov(x, osr).side(0) ## copy next bytes over, b/c going to send them twice
    mov(osr, x).side(0) ## copy next bytes over, b/c going to send them twice
    set(y,15).side(0)  ## send 0, X 
    label("one_time")
    out(pins, 1).side(0)
    jmp(y_dec, "one_time").side(1)
    
    mov(osr,x).side(0) ## copy bytes back 

    set(y,15).side(0)  ## re-send 0, X
    label("one_more_time")
    out(pins, 1).side(0)
    jmp(y_dec, "one_more_time").side(1)

# 16
