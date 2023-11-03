## This file generates headers with lookup tables for various waveforms
## Add your own.

import math

## phase is in degrees: 360 is a full cycle, and this is probably what you want

def phaseSteps(maxPhase, length=256):
    steps = range(0, length) 
    steps = [1.0*x/length * 2.0*math.pi * (maxPhase/360.0) for x in steps]
    return steps

def sine(maxPhase=360, length=256):
    wave = [math.sin(x) for x in phaseSteps(maxPhase, length)]
    return scaleAndRound(wave)

def sawtooth(maxPhase=360, length=256):
    wave = [x for x in range(length)]
    return scaleAndRound(wave)

def square(maxPhase=360, length=256):
    wave = [0]*(length//2)
    wave.extend([1]*(length//2))
    return scaleAndRound(wave)

def triangle(maxPhase=360, length=256):
    wave = [x for x in range(length//2)]
    wave.extend([length//2 - x for x in range(length//2)])
    return scaleAndRound(wave)

def bandlimitedSawtooth(numberPartials, maxPhase=360, length=256):
    wave = [0]*length
    sign = 1.0
    for k in range(1, numberPartials+1):
        phases = phaseSteps(maxPhase*k, length)
        for i in range(length):
            wave[i] += sign * math.sin(phases[i]) / k
        sign = sign * -1
    return scaleAndRound(wave)

def bandlimitedSquare(numberPartials, maxPhase=360, length=256):
    wave = [0]*length
    for k in range(1, numberPartials*2, 2):
        phases = phaseSteps(maxPhase*k, length)
        for i in range(length):
            wave[i] +=  math.sin(phases[i]) / k
    return scaleAndRound(wave)

def bandlimitedTriangle(numberPartials, maxPhase=360, length=256):
    wave = [0]*length
    sign = 1.0
    for k in range(1, numberPartials*2, 2):
        phases = phaseSteps(maxPhase*k, length)
        for i in range(length):
            wave[i] += sign * math.sin(phases[i]) / k**2
        sign = sign * -1
    return scaleAndRound(wave)

def scaleAndRound(data, scale=2**16-1, signedInt=True):
    data = [0.0+x-min(data) for x in data]
    data = [1.0*x/max(data)*scale for x in data]
    data = [int(round(x)) for x in data]
    if signedInt:
        data = [int(x-(scale+1)//2) for x in data]
    return(data)


if __name__ == "__main__":
    
    sawtooth_sample = sawtooth(7)
