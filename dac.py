import logging
from cp2130 import (CP2130, 
                    GpioMode, 
                    GpioState, 
                    SpiCLKRate, 
                    SpiCpha, 
                    SpiCpol, 
                    SpiCSMode)

class Dac:
    MPC_flags = 0x03<<4
    VREF_MV = 3300
    MAX_VALUE = 1<<12
    CS_GPIO = 0

    def __init__(self):
        if CP2130.getNumDevices() == 0:
            logging.error("Couldn't find CP2130 Device!")
            raise IOError
            
        self.cp2130 = CP2130()
        self.cp2130.open()
        self.cp2130.spiConfig(0, SpiCpha.TRAILING_EDGE,
                                SpiCpol.ACTIVE_HIGH,
                                SpiCSMode.PUSH_PULL,
                                SpiCLKRate.SPICTL_CLKRATE_3M)
        self.cp2130.setChipSelect(Dac.CS_GPIO, 2)
        self._currentVoltage = 0
    
    @property
    def currentVoltage(self):
        return self._currentVoltage
    
    @currentVoltage.setter
    def currentVoltage(self, voltage_mv):
        self._currentVoltage = voltage_mv
        value = int(voltage_mv * Dac.MAX_VALUE/Dac.VREF_MV)
        msg = bytearray([(Dac.MPC_flags | ((value & 0xF00) >>8)), value & 0xFF])
        self.cp2130.spiWrite(msg)

