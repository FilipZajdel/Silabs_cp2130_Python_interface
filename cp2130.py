from ctypes import WinDLL, WINFUNCTYPE
from ctypes.wintypes import BYTE,PBYTE, BOOL, WORD, DWORD,UINT, ULONG, PDWORD,HANDLE,PHANDLE

import logging
from enum import IntEnum

cp213x_dll = WinDLL(r'C:\Silabs\MCU\CP2130_SDK\Software\Library\64-bit\SLAB_USB_SPI.dll')

prototype = WINFUNCTYPE(UINT, PDWORD)
CP213x_GetLibraryVersion = prototype(("CP213x_GetLibraryVersion", cp213x_dll))

prototype = WINFUNCTYPE(UINT, PDWORD)
CP213x_GetNumDevices = prototype(("CP213x_GetNumDevices", cp213x_dll))

prototype = WINFUNCTYPE(UINT, DWORD, PHANDLE)
CP213x_OpenByIndex = prototype(("CP213x_OpenByIndex", cp213x_dll))

prototype = WINFUNCTYPE(UINT, HANDLE, BYTE, BYTE)
CP213x_SetChipSelect = prototype(("CP213x_SetChipSelect", cp213x_dll))

prototype = WINFUNCTYPE(UINT, HANDLE, WORD, WORD)
CP213x_SetGpioValues = prototype(("CP213x_SetGpioValues", cp213x_dll))

prototype = WINFUNCTYPE(UINT, HANDLE, PBYTE, DWORD, BOOL, DWORD, PDWORD)
CP213x_TransferWrite = prototype(("CP213x_TransferWrite", cp213x_dll))

prototype = WINFUNCTYPE(UINT, HANDLE, PBYTE, PBYTE, DWORD, BOOL, DWORD, PDWORD)
CP213x_TransferWriteRead = prototype(("CP213x_TransferWriteRead", cp213x_dll))

prototype = WINFUNCTYPE(UINT, HANDLE)
CP213x_Close = prototype(("CP213x_Close", cp213x_dll))

prototype = WINFUNCTYPE(UINT, HANDLE, BYTE)
CP213x_SetClockDivider = prototype(("CP213x_SetClockDivider", cp213x_dll))

prototype = WINFUNCTYPE(UINT, HANDLE, PDWORD)
CP213x_GetGpioValues = prototype(("CP213x_GetGpioValues", cp213x_dll))

prototype = WINFUNCTYPE(UINT, HANDLE, PBYTE, PDWORD)
CP213x_GetEventCounter = prototype(("CP213x_GetEventCounter", cp213x_dll))

prototype = WINFUNCTYPE(UINT, HANDLE, BYTE, BYTE, BYTE)
CP213x_SetGpioModeAndLevel = prototype(("CP213x_SetGpioModeAndLevel", cp213x_dll))

prototype = WINFUNCTYPE(UINT, HANDLE, BYTE, BYTE)
CP213x_SetSpiControlByte = prototype(("CP213x_SetSpiControlByte", cp213x_dll))

class GpioMode(IntEnum):
    GPIO_MODE_INPUT = 0
    GPIO_MODE_OUTPUT_OD = 1
    GPIO_MODE_OUTPUT_PP = 2
    GPIO_MODE_CHIPSELECT = 3

class GpioState(IntEnum):
    LOW = 0
    HIGH = 1

class SpiCpha(IntEnum):
    shift = 5
    LEADING_EDGE = 0
    TRAILING_EDGE = 1

class SpiCpol(IntEnum):
    shift = 4
    ACTIVE_HIGH = 0
    ACTIVE_LOW = 1

class SpiCSMode(IntEnum):
    shift = 3
    OPEN_DRAIN = 0
    PUSH_PULL = 1

class SpiCLKRate(IntEnum):
    shift = 0
    SPICTL_CLKRATE_12M  = 0       
    SPICTL_CLKRATE_6M   = 1       
    SPICTL_CLKRATE_3M   = 2       
    SPICTL_CLKRATE_1M5  = 3       
    SPICTL_CLKRATE_750K = 4      
    SPICTL_CLKRATE_375K = 5       
    SPICTL_CLKRATE_187K5= 6       
    SPICTL_CLKRATE_93K75= 7

class CP2130:
    def __init__(self):
        self.isOpen = False
        self.hDevice=HANDLE(0)
        self.phDevice = PHANDLE(self.hDevice)

    def getNumDevices():
        """ Returns number of connected CP213x devices """
        numDevices = ULONG()
        CP213x_GetNumDevices(PDWORD(numDevices))
        return numDevices.value
    
    def open(self):
        """ Opens CP213x device """
        if CP2130.getNumDevices() == 0 or self.isOpen:
            logging.warning("Device cannot be open")
            return
        
        CP213x_OpenByIndex(DWORD(0), PHANDLE(self.hDevice))
        self.isOpen = True
    
    def close(self):
        """ Closes CP213x device """
        if not self.isOpen:
            return

        CP213x_Close(self.hDevice)
        self.isOpen = False
    
    def spiWrite(self, data: bytearray):
        """ Writes data into SPI bus """
        data=(BYTE*len(data))(*data)
        bytesTransferred = ULONG()
        pBytesActuallyTransferred=PDWORD(bytesTransferred)
        CP213x_TransferWrite(self.hDevice,data,DWORD(len(data)), BOOL(1),DWORD(500), pBytesActuallyTransferred)
        print(f"Transferred {bytesTransferred} bytes")
    
    def setGpio(self, bitmask):
        """ Sets GPIO states """
        gpio_bm = WORD(bitmask)
        CP213x_SetGpioValues(self.phDevice.contents.value, gpio_bm, gpio_bm)
    
    def getGpio(self):
        """ Reads gpio values of device """
        values = DWORD()
        CP213x_GetGpioValues(self.hDevice, PDWORD(values))

        return values.value
    
    def getEventCounter(self):
        """ Gets event counter value """
        WINFUNCTYPE(UINT, HANDLE, PBYTE, PDWORD)
        mode = BYTE()
        counterValue = WORD()
        CP213x_GetEventCounter(self.hDevice, PBYTE(mode), PDWORD(counterValue))
        return counterValue.value
    
    def setGpioValueAndMode(self, gpio_num, gpio_mode, gpio_level):
        """ Sets gpio in certain mode """
        gpio_num = BYTE(gpio_num)
        gpio_mode = BYTE(gpio_mode)
        gpio_level = BYTE(gpio_level)
        CP213x_SetGpioModeAndLevel(self.hDevice, gpio_num, gpio_mode, gpio_level)
    
    def setClkDivider(self, clk_div):
        """ Sets clock divider """
        CP213x_SetClockDivider(self.hDevice, BYTE(clk_div))
    
    def setChipSelect(self, channel, mode):
        """ Sets gpio channel to CHIP Select """
        channel = BYTE(channel)
        mode = BYTE(mode)

        CP213x_SetChipSelect(self.hDevice, channel, mode)
    
    def spiConfig(self, channel, cpha: SpiCpha, cpol: SpiCpol, csmode: SpiCSMode, clkrate: SpiCLKRate):
        """ Configures Spi """
        channel = BYTE(channel)
        chan_config = BYTE(cpha<<SpiCpha.shift | cpol<<SpiCpol.shift | csmode<<SpiCSMode.shift | clkrate<<SpiCLKRate.shift)
        print(chan_config)

        CP213x_SetSpiControlByte(self.hDevice, channel, chan_config)

