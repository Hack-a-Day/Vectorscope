## Hardware GPIO # pin defines

## Screen pins
sck   = const(2)
data  = const(3)
reset = const(4)
dc    = const(5)

## there are a number of libs that require pins that we don't provide
## pass them the on-board LED.  It's unlikely to hurt.
throwaway = const(25)
debug     = const(27)

user_button    = const(19)
audio_shutdown = const(22)

## Codec pins
## clocks
mclk      = const(7)
bit_clock = const(8)
lr_clock  = const(9)
## data
sd_in     = const(13) ## In 3/4 (Y=L, X=R)
sd_out    = const(10) ## Out 1/2 (Y=L, X=R)
## config
pdn       = const(6)
i2c_scl   = const(21)
i2c_sda   = const(20)




## some globally useful pin inits
# debug_pin          = machine.Pin(debug, machine.Pin.OUT, value=0)
# audio_shutdown_pin = machine.Pin(audio_shutdown, machine.Pin.OUT, value=1)
# user_button        = machine.Pin(user_button, machine.Pin.IN)


#sd_in=Pin(13, Pin.IN) ## In 3/4 (Y=L, X=R)
#sd_out=Pin(10, Pin.OUT, value=0) ## Out 1/2 (Y=L, X=R)
