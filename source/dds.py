import array
import generate_wavetables

NUM_SAMPLES      = const(256)
ACCUMULATOR_BITS = const(16)

X_CHANNEL = const(0)
Y_CHANNEL = const(1)

WAVEFORM_SINE     = const(0)
WAVEFORM_SQUARE   = const(1)
WAVEFORM_SAWTOOTH = const(2)
WAVEFORM_TRIANGLE = const(3)


class DDS():

    def __init__(self, vectorscope):
        """ pass it an instance of the Vectorscope module from main, it needs to write to the DMA audio registers""" 
        self.wave = vectorscope.wave

        self.waveform            = ["sine", "sine"]
        self.increment = [51000, 25000]
        self.amplitude           = [1, 1]  ## set this infrequently? -- it's an expensive calculation
        self.phase               = [0, 0]
        self.phase_increment     = [0, 0]  
        self.index               = [0, 0]
        self.accumulator         = [0, 0]
        self.samplesX            = [0]*NUM_SAMPLES
        self.samplesY            = [0]*NUM_SAMPLES
        self.samples             = [self.samplesX, self.samplesY]

        self.base_waveforms = {} 
        self.base_waveforms["sine"] = generate_wavetables.sine()
        self.base_waveforms["square"] = generate_wavetables.square()
        self.base_waveforms["sawtooth"] = generate_wavetables.sawtooth()
        self.base_waveforms["triangle"] = generate_wavetables.triangle()

        ## init
        self.waves = [[0]*256, [0]*256]
        self.recalculate_waveforms()  ## have to do this every time you change parameters.

    def recalculate_waveforms(self):  ## select 0=X, 1=Y
        for i in [0,1]:
            self.waves[i] = [int(self.amplitude[i]*x) for x in self.base_waveforms[self.waveform[i]]]
        
    def initial_wait_for_buffer_sync(self):
        self.wave.outBuffer_ready = False    ## mark seen
        while not self.wave.outBuffer_ready:
            pass   ## (@_@) should be async wait

    @micropython.viper
    def do_dds(self):
        for i in [0,1]:  ## X , Y
            self.phase[i] = int(self.phase[i]) + int(self.phase_increment[i])
            for s in range(NUM_SAMPLES):
                self.index[i] = int(self.phase[i]) + (int(self.accumulator[i]) >> ACCUMULATOR_BITS) & 0xFF ## roll over sample bits
                self.accumulator[i] = (int(self.accumulator[i]) + int(self.increment[i])) & 0xFFFFFF  ## sample bits + accumulator bits
                self.samples[i][s] = self.waves[i][self.index[i]]

    def populate_buffer(self):
        while not self.wave.outBuffer_ready:
            pass   ## (@_@) should be async wait
        self.wave.packX(self.samplesX)
        self.wave.packY(self.samplesY)
        self.wave.outBuffer_ready = False

    
if __name__ == "__main__":
    import vectorscope
    import machine
    userbutton = machine.Pin(19, machine.Pin.IN)

    v = vectorscope.Vectorscope()
    d = DDS(v)
    d.amplitude=[0.5, 0.5]
    d.recalculate_waveforms()
    ## but you can also write them yourself directly: 16-bit signed, 256 values
    d.waves[0] = [0]*256
    ## but it gets overwritten if you recalculate_waveforms()
    d.recalculate_waveforms()

    
    def go(n=200):
        for i in range(n):
            d.do_dds()
            d.populate_buffer()
        d.waves[0] = d.base_waveforms["square"] 
        d.recalculate_waveforms()

            
        for i in range(n):
            d.do_dds()
            d.populate_buffer()

    go()








        




