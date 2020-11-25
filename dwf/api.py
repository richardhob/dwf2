#! /usr/bin/env python
# -*- coding: utf-8 -*-

from enum import IntEnum

from . import lowlevel as _l

#################################################################
# Class-based APIs
#################################################################

def _make_set(value, enum):
    ''' Helper function which turns the input `value` into a tuple of enums.

    Args:
        value (int): Raw register value / result from the device
        enum (IntEnum): Enumeration which describes the bits in the value

    Returns:
        tuple of enums
    '''
    result = []
    for e in list(enum):
        if _l.IsBitSet(value, e.value):
            result.append(e)
    return frozenset(result)

# DEVICE MANAGMENT FUNCTIONS
# Enumeration:
class ENUMFILTER(IntEnum):
    '''DwfEnumeration filter options'''
    ALL       = _l.enumfilterAll
    EEXPLORER = _l.enumfilterEExplorer
    DISCOVERY = _l.enumfilterDiscovery

def DwfEnumeration(enumfilter=ENUMFILTER.ALL):
    '''Enumerate the connected DWF devices.

    Example:
        >>> dwf.DwfEnumeration(dwf.ENUMFILTER.ALL)
        (...)

    Args:
        enumfilter (dwf.ENUMFILTER): Device type to enuemrate. Options are:
            - dwf.ENUMFILTER.ALL
            - dwf.ENUMFILTER.EEXPLORER
            - dwf.ENUMFILTER.DISCOVERY

    Returns:
        tuple of dwf.DwfDevice values
    '''
    num = _l.FDwfEnum(enumfilter)
    return tuple([DwfDevice(i) for i in range(num)])

class DwfDevice(object):
    '''DWF Device instance, which contains information about:

    - What type of device this is
    - Device index in the Enumeration
    - Device configuration

    This class is returned when `DwfEnumeration` is called with devices
    connected:

    Example:
    >>> devices = dwf.DwfEnumeration()
    >>> dev = devices[0]
    >>> dev.name()
    'Analog Discovery'
    >>> dev.SN()
    'SN:210244516509'
    >>> dev.configInfo(dev.CONFIGINFO.ANALOG_IN_CHANNEL_COUNT)
    2
    >>> dwf = dev.open() # Open the selected device

    Args:
        idxDevice (int): Device index from the DWF Enumeration.
    '''
    class DEVID(IntEnum):
        '''Device type (returned from deviceType)'''
        EEXPLORER                   = _l.devidEExplorer
        DISCOVERY                   = _l.devidDiscovery

    class DEVVER(IntEnum):
        '''Device version (returned from deviceType)'''
        EEXPLORER_C                 = _l.devverEExplorerC
        EEXPLORER_E                 = _l.devverEExplorerE
        EEXPLORER_F                 = _l.devverEExplorerF
        DISCOVERY_A                 = _l.devverDiscoveryA
        DISCOVERY_B                 = _l.devverDiscoveryB
        DISCOVERY_C                 = _l.devverDiscoveryC

    class CONFIGINFO(IntEnum):
        '''Device Configuration Details, used with configInfo'''
        ANALOG_IN_CHANNEL_COUNT     = _l.DECIAnalogInChannelCount
        ANALOG_OUT_CHANNEL_COUNT    = _l.DECIAnalogOutChannelCount
        ANALOG_IO_CHANNEL_COUNT     = _l.DECIAnalogIOChannelCount
        DIGITAL_IN_CHANNEL_COUNT    = _l.DECIDigitalInChannelCount
        DIGITAL_OUT_CHANNEL_COUNT   = _l.DECIDigitalOutChannelCount
        DIGITAL_IO_CHANNEL_COUNT    = _l.DECIDigitalIOChannelCount
        ANALOG_IN_BUFFER_SIZE       = _l.DECIAnalogInBufferSize
        ANALOG_OUT_BUFFER_SIZE      = _l.DECIAnalogOutBufferSize
        DIGITAL_IN_BUFFER_SIZE      = _l.DECIDigitalInBufferSize
        DIGITAL_OUT_BUFFER_SIZE     = _l.DECIDigitalOutBufferSize

    def __init__(self, idxDevice):
        super(DwfDevice, self).__init__()
        self.idxDevice = idxDevice

    def deviceType(self):
        ''' Get the Device Type from the `FDwfEnumDeviceType` low level
        function.

        Returns:
            Device Id and Device Version (as Enums)
        '''
        devid, devver = _l.FDwfEnumDeviceType(self.idxDevice)
        return self.DEVID(devid), self.DEVVER(devver)

    def isOpened(self):
        ''' Is this device open?

        Returns:
            True if open, False otherwise.
        '''
        return bool(_l.FDwfEnumDeviceIsOpened(self.idxDevice))

    def userName(self):
        ''' Get the Device's User set name

        Returns:
            Retreived Name as a string.
        '''
        return _l.FDwfEnumUserName(self.idxDevice)

    def deviceName(self):
        ''' Get the Device's name.

        Returns:
            Retreived Name as a string.
        '''
        return _l.FDwfEnumDeviceName(self.idxDevice)

    def SN(self):
        ''' Get the Device's serial number.

        Returns:
            Serial Nmber as a string.
        '''
        return _l.FDwfEnumSN(self.idxDevice)

    def config(self):
        ''' Get the device's configuration.

        Returns:
            Device configuration as an integer.
        '''
        return _l.FDwfEnumConfig(self.idxDevice)

    def configInfo(self, info):
        ''' Get the device's configuration information, based on the input
        `info` parameter.

        Args:
            info (dwf.DwfDevice.CONFIGINFO): Device configuration parameter to
                get information about.

        Returns:
            Number of features corresponding to the input info as an integer
        '''
        return _l.FDwfEnumConfigInfo(self.idxDevice, info)

    def open(self, config=None):
        '''Open this device.

        Args:
            config (int): Configuration to use. Default is None, which uses the
                current configuration.

        Returns:
            dwf.Dwf device.
        '''
        return Dwf(self.idxDevice, idxCfg=config)

class _HDwf(object):
    '''Context manager for the DWF Hardware pointer, which automatically closes
    the connection upon deletion.

    This also implements the _as_parameter_ "ctypes" special attribute, which
    automatically passes the HDWF context to CTYPES functions (so the DWF SDK
    functions in the DLL). Which is neat.

    This is instantiated in the `dwf.Dwf` class.

    Args:
        hdwf: Hardware context from FDwfDeviceOpen.
    '''
    def __init__(self, hdwf):
        super(_HDwf, self).__init__()
        self.hdwf = hdwf

    @property
    def _as_parameter_(self):
        '''Special CTYPES attribute - pass the HDWF to the CTYPES functions when
        used as a parameter.'''
        return self.hdwf

    def close(self):
        '''Close the Hardware context if it is valid.'''
        if self.hdwf != _l.hdwfNone:
            _l.FDwfDeviceClose(self.hdwf)
            self.hdwf = _l.hdwfNone

    def __del__(self):
        self.close()

class Dwf(object):
    ''' Main DWF device wrapper.

    This class is used to configure the Hardware context, as well as configure
    Triggers for various things.

    Example:
    >>> devices = dwf.DwfEnumerate()
    >>> dev = devices[0].open() # get the DWF device for the enumerated devices

    Example:
    >>> dev = dwf.Dwf() # Get the first found device

    Args:
        idxDevice (int): Device index to open. If set to '-1', the first found
            device will be used. Default is '-1'.
        idxCfg (int): Device configuration to use. The Device configuration can
            be found in the Waveforms GUI / Device Manager. Default is None (ie
            use the current configuration)
    '''
    DEVICE_NONE             = _l.hdwfNone

    class TRIGSRC(IntEnum):
        '''Trigger sources'''
        NONE                = _l.trigsrcNone
        PC                  = _l.trigsrcPC
        DETECTOR_ANALOG_IN  = _l.trigsrcDetectorAnalogIn
        DETECTOR_DIGITAL_IN = _l.trigsrcDetectorDigitalIn
        ANALOG_IN           = _l.trigsrcAnalogIn
        DIGITAL_IN          = _l.trigsrcDigitalIn
        DIGITAL_OUT         = _l.trigsrcDigitalOut
        ANALOG_OUT1         = _l.trigsrcAnalogOut1
        ANALOG_OUT2         = _l.trigsrcAnalogOut2
        ANALOG_OUT3         = _l.trigsrcAnalogOut3
        ANALOG_OUT4         = _l.trigsrcAnalogOut4
        EXTERNAL1           = _l.trigsrcExternal1
        EXTERNAL2           = _l.trigsrcExternal2
        EXTERNAL3           = _l.trigsrcExternal3
        EXTERNAL4           = _l.trigsrcExternal4

    class STATE(IntEnum):
        '''instrument states'''
        READY               = _l.DwfStateReady
        CONFIG              = _l.DwfStateConfig
        PREFILL             = _l.DwfStatePrefill
        ARMED               = _l.DwfStateArmed
        WAIT                = _l.DwfStateWait
        TRIGGERED           = _l.DwfStateTriggered
        RUNNING             = _l.DwfStateRunning
        DONE                = _l.DwfStateDone

    def __init__(self, idxDevice=-1, idxCfg=None):
        super(Dwf, self).__init__()

        # Not sure why this is needed - should never call with a Dwf class
        if isinstance(idxDevice, Dwf):
            raise ValueError("idxDevice cannot be an instance of Dwf")

        # Also not sure why this is needed? DwfDevice uses the device index to
        # instantiate an instance of this class
        if isinstance(idxDevice, DwfDevice):
            idxDevice = idxDevice.idxDevice

        if idxCfg is None:
            hdwf = _l.FDwfDeviceOpen(idxDevice)
        else:
            hdwf = _l.FDwfDeviceConfigOpen(idxDevice, idxCfg)

        if hdwf == self.DEVICE_NONE:
            raise RuntimeError("Device is not found")

        self.hdwf = _HDwf(hdwf)

    def close(self):
        '''Close the HDWF instance.'''
        self.hdwf.close()

    def autoConfigureSet(self, auto_configure):
        '''Enable or disable Autoconfiguration of the device.

        When this setting is enabled, the device is automatically configured
        every time an instrument parameter is set.

        For example, when AutoConfigure is enabled, FDwfAnalogOutConfigure does
        not need to be called after FDwfAnalogOutRunSet. This adds latency to
        every Set function; just as much latency as calling the corresponding
        Configure function directly afterward.

        Args:
            auto_configure (bool): True -> Enable, False -> Disable
        '''
        _l.FDwfDeviceAutoConfigureSet(self.hdwf, auto_configure)

    def autoConfigureGet(self):
        '''Get the AutoConfigure setting.

        Returns:
            True if Auto Configuration is enabled, False otherwise.
        '''
        return bool(_l.FDwfDeviceAutoConfigureGet(self.hdwf))

    def reset(self):
        '''Reset the Device, and configure all device and instrument parameters
        to default values.'''
        _l.FDwfDeviceReset(self.hdwf)

    def enableSet(self, enable):
        '''Not sure what this does - Enable / Disable the device maybe?'''
        _l.FDwfDeviceEnableSet(self.hdwf, enable)

    def triggerInfo(self):
        '''Return the supported trigger source options for the global trigger
        bus.

        The Global trigger bus allows for multiple instruments (or devices) to
        trigger each other.

        See dwf.Dwf.TRIGSRC for a list of triggers.

        Retuns:
            Frozen set of Trigger sources.
        '''
        return _make_set(_l.FDwfDeviceTriggerInfo(self.hdwf), self.TRIGSRC)

    def triggerSet(self, idxPin, trigsrc):
        '''Set the Global trigger source to use the selected External IO Trigger
        / trigger source.

        Args:
            idxPIn (int): External Trigger, I/O pin index.
            trigsrc (dwf.Dwf.TRIGSRC): Trigger source selection.
        '''
        _l.FDwfDeviceTriggerSet(self.hdwf, idxPin, trigsrc)

    def triggerGet(self, idxPin):
        '''Get the trigger source set on the external trigger pin.

        Args:
            idxPIn (int): External Trigger, I/O pin index.

        Returns:
            Trigger source configured (dwf.Dwf.TRIGSRC)
        '''
        return self.TRIGSRC(_l.FDwfDeviceTriggerGet(self.hdwf, idxPin))

    def triggerPC(self):
        '''Generate one pulse on the PC trigger line'''
        _l.FDwfDeviceTriggerPC(self.hdwf)

# ANALOG IN INSTRUMENT FUNCTIONS
class DwfAnalogIn(Dwf):
    class ACQMODE(IntEnum):
        '''acquisition modes'''
        SINGLE = _l.acqmodeSingle
        SCAN_SHIFT = _l.acqmodeScanShift
        SCAN_SCREEN = _l.acqmodeScanScreen
        RECORD = _l.acqmodeRecord

    class FILTER(IntEnum):
        '''analog acquisition filter'''
        DECIMATE = _l.filterDecimate
        AVERAGE = _l.filterAverage
        MIN_MAX = _l.filterMinMax

    class TRIGTYPE(IntEnum):
        '''analog in trigger mode'''
        EDGE = _l.trigtypeEdge
        PULSE = _l.trigtypePulse
        TRANSITION = _l.trigtypeTransition

    class TRIGCOND(IntEnum):
        '''analog in trigger condition'''
        RISING_POSITIVE = _l.trigcondRisingPositive
        FALLING_NEGATIVE = _l.trigcondFallingNegative

    class TRIGLEN(IntEnum):
        '''analog in trigger length condition'''
        LESS = _l.triglenLess
        TIMEOUT = _l.triglenTimeout
        MORE = _l.triglenMore

# Control and status:
    def __init__(self, idxDevice=-1, idxCfg=None):
        if isinstance(idxDevice, Dwf):
            self.hdwf = idxDevice.hdwf
        else:
            super(DwfAnalogIn, self).__init__(idxDevice, idxCfg)
    def reset(self, parent=False):
        if parent: super(DwfAnalogIn, self).reset()
        _l.FDwfAnalogInReset(self.hdwf)
    def configure(self, reconfigure, start):
        _l.FDwfAnalogInConfigure(self.hdwf, reconfigure, start)
    def status(self, read_data):
        return self.STATE(_l.FDwfAnalogInStatus(self.hdwf, read_data))
    def statusSamplesLeft(self):
        return _l.FDwfAnalogInStatusSamplesLeft(self.hdwf)
    def statusSamplesValid(self):
        return _l.FDwfAnalogInStatusSamplesValid(self.hdwf)
    def statusIndexWrite(self):
        return _l.FDwfAnalogInStatusIndexWrite(self.hdwf)
    def statusAutotriggered(self):
        return bool(_l.FDwfAnalogInStatusAutoTriggered(self.hdwf))
    def statusData(self, idxChannel, data_num):
        return _l.FDwfAnalogInStatusData(self.hdwf, idxChannel, data_num)
    def statusNoise(self, idxChannel, data_num):
        return _l.FDwfAnalogInStatusNoise(self.hdwf, idxChannel, data_num)
    def statusSample(self, idxChannel):
        return _l.FDwfAnalogInStatusSample(self.hdwf, idxChannel)
    def statusRecord(self):
        return _l.FDwfAnalogInStatusRecord(self.hdwf)
    def recordLengthSet(self, length):
        _l.FDwfAnalogInRecordLengthSet(self.hdwf, length)
    def recordLengthGet(self):
        return _l.FDwfAnalogInRecordLengthGet(self.hdwf)

# Acquisition configuration:
    def frequencyInfo(self):
        return _l.FDwfAnalogInFrequencyInfo(self.hdwf)
    def frequencySet(self, hzFrequency):
        _l.FDwfAnalogInFrequencySet(self.hdwf, hzFrequency)
    def frequencyGet(self):
        return _l.FDwfAnalogInFrequencyGet(self.hdwf)
    def bitsInfo(self):
        '''Returns the number of ADC bits'''
        return _l.FDwfAnalogInBitsInfo(self.hdwf)

    def bufferSizeInfo(self):
        return _l.FDwfAnalogInBufferSizeInfo(self.hdwf)
    def bufferSizeSet(self, size):
        _l.FDwfAnalogInBufferSizeSet(self.hdwf, size)
    def bufferSizeGet(self):
        return _l.FDwfAnalogInBufferSizeGet(self.hdwf)

    def noiseSizeInfo(self):
        return _l.FDwfAnalogInNoiseSizeInfo(self.hdwf)
    def noiseSizeGet(self):
        return _l.FDwfAnalogInNoiseSizeGet(self.hdwf)

    def acquisitionModeInfo(self):
        return _make_set(
            _l.FDwfAnalogInAcquisitionModeInfo(self.hdwf), self.ACQMODE)
    def acquisitionModeSet(self, acqmode):
        _l.FDwfAnalogInAcquisitionModeSet(self.hdwf, acqmode)
    def acquisitionModeGet(self):
        return self.ACQMODE(_l.FDwfAnalogInAcquisitionModeGet(self.hdwf))

# Channel configuration:
    def channelCount(self):
        return _l.FDwfAnalogInChannelCount(self.hdwf)
    def channelEnableSet(self, idxChannel, enable):
        _l.FDwfAnalogInChannelEnableSet(self.hdwf, idxChannel, enable)
    def channelEnableGet(self, idxChannel):
        return bool(_l.FDwfAnalogInChannelEnableGet(self.hdwf, idxChannel))
    def channelFilterInfo(self):
        return _make_set(
            _l.FDwfAnalogInChannelFilterInfo(self.hdwf), self.FILTER)
    def channelFilterSet(self, idxChannel, filter_):
        _l.FDwfAnalogInChannelFilterSet(self.hdwf, idxChannel, filter_)
    def channelFilterGet(self, idxChannel):
        return self.FILTER(_l.FDwfAnalogInChannelFilterGet(
            self.hdwf, idxChannel))
    def channelRangeInfo(self):
        return _l.FDwfAnalogInChannelRangeInfo(self.hdwf)
    def channelRangeSteps(self):
        return _l.FDwfAnalogInChannelRangeSteps(self.hdwf)
    def channelRangeSet(self, idxChannel, voltsRange):
        _l.FDwfAnalogInChannelRangeSet(self.hdwf, idxChannel, voltsRange)
    def channelRangeGet(self, idxChannel):
        return _l.FDwfAnalogInChannelRangeGet(self.hdwf, idxChannel)
    def channelOffsetInfo(self):
        return _l.FDwfAnalogInChannelOffsetInfo(self.hdwf)
    def channelOffsetSet(self, idxChannel, voltOffset):
        _l.FDwfAnalogInChannelOffsetSet(self.hdwf, idxChannel, voltOffset)
    def channelOffsetGet(self, idxChannel):
        return _l.FDwfAnalogInChannelOffsetGet(self.hdwf, idxChannel)
    def channelAttenuationSet(self, idxChannel, attenuation):
        _l.FDwfAnalogInChannelAttenuationSet(self.hdwf, idxChannel, attenuation)
    def channelAttenuationGet(self, idxChannel):
        return _l.FDwfAnalogInChannelAttenuationGet(self.hdwf, idxChannel)

# Trigger configuration:
    def triggerSourceInfo(self):
        return _make_set(
            _l.FDwfAnalogInTriggerSourceInfo(self.hdwf), self.TRIGSRC)
    def triggerSourceSet(self, trigsrc):
        _l.FDwfAnalogInTriggerSourceSet(self.hdwf, trigsrc)
    def triggerSourceGet(self):
        return self.TRIGSRC(_l.FDwfAnalogInTriggerSourceGet(self.hdwf))

    def triggerPositionInfo(self):
        return _l.FDwfAnalogInTriggerPositionInfo(self.hdwf)
    def triggerPositionSet(self, secPosition):
        _l.FDwfAnalogInTriggerPositionSet(self.hdwf, secPosition)
    def triggerPositionGet(self):
        return _l.FDwfAnalogInTriggerPositionGet(self.hdwf)
    def triggerPositionStatus(self):
        return _l.FDwfAnalogInTriggerPositionStatus(self.hdwf)

    def triggerAutoTimeoutInfo(self):
        return _l.FDwfAnalogInTriggerAutoTimeoutInfo(self.hdwf)
    def triggerAutoTimeoutSet(self, secTimeout):
        _l.FDwfAnalogInTriggerAutoTimeoutSet(self.hdwf, secTimeout)
    def triggerAutoTimeoutGet(self):
        return _l.FDwfAnalogInTriggerAutoTimeoutGet(self.hdwf)

    def triggerHoldOffInfo(self):
        return _l.FDwfAnalogInTriggerHoldOffInfo(self.hdwf)
    def triggerHoldOffSet(self, secHoldOff):
        _l.FDwfAnalogInTriggerHoldOffSet(self.hdwf, secHoldOff)
    def triggerHoldOffGet(self):
        return _l.FDwfAnalogInTriggerHoldOffGet(self.hdwf)

    def triggerTypeInfo(self):
        return _make_set(
            _l.FDwfAnalogInTriggerTypeInfo(self.hdwf), self.TRIGTYPE)
    def triggerTypeSet(self, trigtype):
        _l.FDwfAnalogInTriggerTypeSet(self.hdwf, trigtype)
    def triggerTypeGet(self):
        return self.TRIGTYPE(_l.FDwfAnalogInTriggerTypeGet(self.hdwf))

    def triggerChannelInfo(self):
        return _l.FDwfAnalogInTriggerChannelInfo(self.hdwf)
    def triggerChannelSet(self, idxChannel):
        _l.FDwfAnalogInTriggerChannelSet(self.hdwf, idxChannel)
    def triggerChannelGet(self):
        return _l.FDwfAnalogInTriggerChannelGet(self.hdwf)

    def triggerFilterInfo(self):
        return _make_set(
            _l.FDwfAnalogInTriggerFilterInfo(self.hdwf), self.FILTER)
    def triggerFilterSet(self, filter_):
        _l.FDwfAnalogInTriggerFilterSet(self.hdwf, filter_)
    def triggerFilterGet(self):
        return self.FILTER(_l.FDwfAnalogInTriggerFilterGet(self.hdwf))

    def triggerLevelInfo(self):
        return _l.FDwfAnalogInTriggerLevelInfo(self.hdwf)
    def triggerLevelSet(self, voltsLevel):
        _l.FDwfAnalogInTriggerLevelSet(self.hdwf, voltsLevel)
    def triggerLevelGet(self):
        return _l.FDwfAnalogInTriggerLevelGet(self.hdwf)

    def triggerHysteresisInfo(self):
        return _l.FDwfAnalogInTriggerHysteresisInfo(self.hdwf)
    def triggerHysteresisSet(self, voltsLevel):
        _l.FDwfAnalogInTriggerHysteresisSet(self.hdwf, voltsLevel)
    def triggerHysteresisGet(self):
        return _l.FDwfAnalogInTriggerHysteresisGet(self.hdwf)

    def triggerConditionInfo(self):
        return _make_set(
            _l.FDwfAnalogInTriggerConditionInfo(self.hdwf), self.TRIGCOND)
    def triggerConditionSet(self, trigcond):
        _l.FDwfAnalogInTriggerConditionSet(self.hdwf, trigcond)
    def triggerConditionGet(self):
        return self.TRIGCOND(_l.FDwfAnalogInTriggerConditionGet(self.hdwf))

    def triggerLengthInfo(self):
        return _l.FDwfAnalogInTriggerLengthInfo(self.hdwf)
    def triggerLengthSet(self, secLength):
        _l.FDwfAnalogInTriggerLengthSet(self.hdwf, secLength)
    def triggerLengthGet(self):
        return _l.FDwfAnalogInTriggerLengthGet(self.hdwf)

    def triggerLengthConditionInfo(self):
        return _make_set(
            _l.FDwfAnalogInTriggerLengthConditionInfo(self.hdwf), self.TRIGLEN)
    def triggerLengthConditionSet(self, triglen):
        _l.FDwfAnalogInTriggerLengthConditionSet(self.hdwf, triglen)
    def triggerLengthConditionGet(self):
        return self.TRIGLEN(_l.FDwfAnalogInTriggerLengthConditionGet(self.hdwf))


# ANALOG OUT INSTRUMENT FUNCTIONS
class DwfAnalogOut(Dwf):
    class FUNC(IntEnum):
        '''analog out signal types'''
        DC = _l.funcDC
        SINE = _l.funcSine
        SQUARE = _l.funcSquare
        TRIANGLE = _l.funcTriangle
        RAMP_UP = _l.funcRampUp
        RAMP_DOWN = _l.funcRampDown
        NOISE = _l.funcNoise
        CUSTOM = _l.funcCustom
        PLAY = _l.funcPlay

    class NODE(IntEnum):
        CARRIER = _l.AnalogOutNodeCarrier
        FM = _l.AnalogOutNodeFM
        AM = _l.AnalogOutNodeAM

    class MODE(IntEnum):
        VOLTAGE = _l.DwfAnalogOutModeVoltage
        CURRENT = _l.DwfAnalogOutModeCurrent

    class IDLE(IntEnum):
        DISABLE = _l.DwfAnalogOutIdleDisable
        OFFSET = _l.DwfAnalogOutIdleOffset
        INITIAL = _l.DwfAnalogOutIdleInitial

# Configuration:
    def channelCount(self): # changed names
        return _l.FDwfAnalogOutCount(self.hdwf)

    def masterSet(self, idxChannel, idxMaster):
        _l.FDwfAnalogOutMasterSet(self.hdwf, idxChannel, idxMaster)
    def masterGet(self, idxChannel):
        return _l.FDwfAnalogOutMasterGet(self.hdwf, idxChannel)

    def triggerSourceInfo(self, idxChannel):
        return _make_set(
            _l.FDwfAnalogOutTriggerSourceInfo(self.hdwf, idxChannel),
            self.TRIGSRC)
    def triggerSourceSet(self, idxChannel, trigsrc):
        _l.FDwfAnalogOutTriggerSourceSet(self.hdwf, idxChannel, trigsrc)
    def triggerSourceGet(self, idxChannel):
        return self.TRIGSRC(
            _l.FDwfAnalogOutTriggerSourceGet(self.hdwf, idxChannel))

    def runInfo(self, idxChannel):
        return _l.FDwfAnalogOutRunInfo(self.hdwf, idxChannel)
    def runSet(self, idxChannel, secRun):
        _l.FDwfAnalogOutRunSet(self.hdwf, idxChannel, secRun)
    def runGet(self, idxChannel):
        return _l.FDwfAnalogOutRunGet(self.hdwf, idxChannel)
    def runStatus(self, idxChannel):
        return _l.FDwfAnalogOutRunStatus(self.hdwf, idxChannel)

    def waitInfo(self, idxChannel):
        return _l.FDwfAnalogOutWaitInfo(self.hdwf, idxChannel)
    def waitSet(self, idxChannel, secWait):
        _l.FDwfAnalogOutWaitSet(self.hdwf, idxChannel, secWait)
    def waitGet(self, idxChannel):
        return _l.FDwfAnalogOutWaitGet(self.hdwf, idxChannel)

    def repeatInfo(self, idxChannel):
        return _l.FDwfAnalogOutRepeatInfo(self.hdwf, idxChannel)
    def repeatSet(self, idxChannel, repeat):
        _l.FDwfAnalogOutRepeatSet(self.hdwf, idxChannel, repeat)
    def repeatGet(self, idxChannel):
        return _l.FDwfAnalogOutRepeatGet(self.hdwf, idxChannel)
    def repeatStatus(self, idxChannel):
        return _l.FDwfAnalogOutRepeatStatus(self.hdwf, idxChannel)

    def repeatTriggerSet(self, idxChannel, repeat_trigger):
        _l.FDwfAnalogOutRepeatTriggerSet(self.hdwf, idxChannel, repeat_trigger)
    def repeatTriggerGet(self, idxChannel):
        return bool(_l.FDwfAnalogOutRepeatTriggerGet(self.hdwf, idxChannel))

    # EExplorer channel 3&4 current/voltage limitation
    def limitationInfo(self, idxChannel):
        return _l.FDwfAnalogOutLimitationInfo(self.hdwf, idxChannel)
    def limitationSet(self, idxChannel, limit):
        _l.FDwfAnalogOutLimitationSet(self.hdwf, idxChannel, limit)
    def limitationGet(self, idxChannel):
        return _l.FDwfAnalogOutLimitationGet(self.hdwf, idxChannel)

    def modeSet(self, idxChannel, mode):
        _l.FDwfAnalogOutModeSet(self.hdwf, idxChannel, mode)
    def modeGet(self, idxChannel):
        return self.MODE(_l.FDwfAnalogOutModeGet(self.hdwf, idxChannel))

    def idleInfo(self, idxChannel):
        return _make_set(
            _l.FDwfAnalogOutIdleInfo(self.hdwf, idxChannel), self.IDLE)
    def idleSet(self, idxChannel, idle):
        _l.FDwfAnalogOutIdleSet(self.hdwf, idxChannel, idle)
    def idleGet(self, idxChannel):
        return self.IDLE(_l.FDwfAnalogOutIdleGet(self.hdwf, idxChannel))

    def nodeInfo(self, idxChannel):
        '''use IsBitSet'''
        return _make_set(
            _l.FDwfAnalogOutNodeInfo(self.hdwf, idxChannel), self.NODE)

    def nodeEnableSet(self, idxChannel, node, enable):
        _l.FDwfAnalogOutNodeEnableSet(self.hdwf, idxChannel, node, enable)
    def nodeEnableGet(self, idxChannel, node):
        return bool(_l.FDwfAnalogOutNodeEnableGet(self.hdwf, idxChannel, node))

    def nodeFunctionInfo(self, idxChannel, node):
        return _make_set(
            _l.FDwfAnalogOutNodeFunctionInfo(self.hdwf, idxChannel, node),
            self.FUNC)
    def nodeFunctionSet(self, idxChannel, node, func):
        _l.FDwfAnalogOutNodeFunctionSet(self.hdwf, idxChannel, node, func)
    def nodeFunctionGet(self, idxChannel, node):
        return self.FUNC(
            _l.FDwfAnalogOutNodeFunctionGet(self.hdwf, idxChannel, node))

    def nodeFrequencyInfo(self, idxChannel, node):
        return _l.FDwfAnalogOutNodeFrequencyInfo(self.hdwf, idxChannel, node)
    def nodeFrequencySet(self, idxChannel, node, hzFrequency):
        _l.FDwfAnalogOutNodeFrequencySet(
            self.hdwf, idxChannel, node, hzFrequency)
    def nodeFrequencyGet(self, idxChannel, node):
        return _l.FDwfAnalogOutNodeFrequencyGet(self.hdwf, idxChannel, node)

# Carrier Amplitude or Modulation Index
    def nodeAmplitudeInfo(self, idxChannel, node):
        return _l.FDwfAnalogOutNodeAmplitudeInfo(self.hdwf, idxChannel, node)
    def nodeAmplitudeSet(self, idxChannel, node, amplitude):
        _l.FDwfAnalogOutNodeAmplitudeSet(self.hdwf, idxChannel, node, amplitude)
    def nodeAmplitudeGet(self, idxChannel, node):
        return _l.FDwfAnalogOutNodeAmplitudeGet(self.hdwf, idxChannel, node)

    def nodeModulationInfo(self, idxChannel, node):
        return _l.FDwfAnalogOutNodeAmplitudeInfo(self, idxChannel, node)
    def nodeModulationSet(self, idxChannel, node, modulation):
        _l.FDwfAnalogOutNodeAmplitudeSet(
            self.hdwf, idxChannel, node, modulation)
    def nodeModulationGet(self, idxChannel, node):
        return _l.FDwfAnalogOutNodeAmplitudeGet(self.hdwf, idxChannel, node)

    def nodeOffsetInfo(self, idxChannel, node):
        return _l.FDwfAnalogOutNodeOffsetInfo(self.hdwf, idxChannel, node)
    def nodeOffsetSet(self, idxChannel, node, offset):
        _l.FDwfAnalogOutNodeOffsetSet(self.hdwf, idxChannel, node, offset)
    def nodeOffsetGet(self, idxChannel, node):
        return _l.FDwfAnalogOutNodeOffsetGet(self.hdwf, idxChannel, node)

    def nodeSymmetryInfo(self, idxChannel, node):
        return _l.FDwfAnalogOutNodeSymmetryInfo(self.hdwf, idxChannel, node)
    def nodeSymmetrySet(self,  idxChannel, node, percentageSymmetry):
        _l.FDwfAnalogOutNodeSymmetrySet(
            self.hdwf, idxChannel, node, percentageSymmetry)
    def nodeSymmetryGet(self,  idxChannel, node):
        return _l.FDwfAnalogOutNodeSymmetryGet(self.hdwf, idxChannel, node)

    def nodePhaseInfo(self, idxChannel, node):
        return _l.FDwfAnalogOutNodePhaseInfo(self.hdwf, idxChannel, node)
    def nodePhaseSet(self, idxChannel, node, degreePhase):
        _l.FDwfAnalogOutNodePhaseSet(self.hdwf, idxChannel, node, degreePhase)
    def nodePhaseGet(self, idxChannel, node):
        return _l.FDwfAnalogOutNodePhaseGet(self.hdwf, idxChannel, node)

    def nodeDataInfo(self, idxChannel, node):
        return _l.FDwfAnalogOutNodeDataInfo(self.hdwf, idxChannel, node)
    def nodeDataSet(self, idxChannel, node, rgdData):
        _l.FDwfAnalogOutNodeDataSet(self.hdwf, idxChannel, node, rgdData)

# needed for EExplorer, don't care for ADiscovery
    def customAMFMEnableSet(self, idxChannel, enable):
        _l.FDwfAnalogOutCustomAMFMEnableSet(self.hdwf, idxChannel, enable)
    def customAMFMEnableGet(self, idxChannel):
        return bool(_l.FDwfAnalogOutCustomAMFMEnableGet(self.hdwf, idxChannel))

# Control:
    def __init__(self, idxDevice=-1, idxCfg=None):
        if isinstance(idxDevice, Dwf):
            self.hdwf = idxDevice.hdwf
        else:
            super(DwfAnalogOut, self).__init__(idxDevice, idxCfg)
    def reset(self, idxChannel=-1, parent=False):
        if parent: super(DwfAnalogIn, self).reset()
        _l.FDwfAnalogOutReset(self.hdwf, idxChannel)
    def configure(self, idxChannel, start):
        _l.FDwfAnalogOutConfigure(self.hdwf, idxChannel, start)
    def status(self, idxChannel):
        return self.STATE(_l.FDwfAnalogOutStatus(self.hdwf, idxChannel))
    def nodePlayStatus(self, idxChannel, node):
        return _l.FDwfAnalogOutNodePlayStatus(self.hdwf, idxChannel, node)
    def nodePlayData(self, idxChannel, node, rgdData):
        _l.FDwfAnalogOutNodePlayData(self.hdwf, idxChannel, node, rgdData)

# ANALOG IO INSTRUMENT FUNCTIONS
class DwfAnalogIO(Dwf):
    class TYPE(IntEnum):
        '''analog io channel node types'''
        ENABLE = _l.analogioEnable
        VOLTAGE = _l.analogioVoltage
        CURRENT = _l.analogioCurrent
        POWER = _l.analogioPower
        TEMPERATURE = _l.analogioTemperature

# Control:
    def __init__(self, idxDevice=-1, idxCfg=None):
        if isinstance(idxDevice, Dwf):
            self.hdwf = idxDevice.hdwf
        else:
            super(DwfAnalogIO, self).__init__(idxDevice, idxCfg)
    def reset(self, parent=False):
        if parent: super(DwfAnalogIO, self).reset()
        _l.FDwfAnalogIOReset(self.hdwf)
    def configure(self):
        return _l.FDwfAnalogIOConfigure(self.hdwf)
    def status(self):
        _l.FDwfAnalogIOStatus(self.hdwf)

# Configure:
    def enableInfo(self):
        return bool(_l.FDwfAnalogIOEnableInfo(self.hdwf))
    def enableSet(self, master_enable):
        _l.FDwfAnalogIOEnableSet(self.hdwf, master_enable)
    def enableGet(self):
        return bool(_l.FDwfAnalogIOEnableGet(self.hdwf))
    def enableStatus(self):
        return bool(_l.FDwfAnalogIOEnableStatus(self.hdwf))

    def channelCount(self):
        return _l.FDwfAnalogIOChannelCount(self.hdwf)
    def channelName(self, idxChannel):
        return _l.FDwfAnalogIOChannelName(self.hdwf, idxChannel)
    def channelInfo(self, idxChannel):
        return _l.FDwfAnalogIOChannelInfo(self.hdwf, idxChannel)

    def channelNodeName(self, idxChannel, idxNode):
        return _l.FDwfAnalogIOChannelNodeName(self.hdwf, idxChannel, idxNode)
    def channelNodeInfo(self, idxChannel, idxNode):
        result = _l.FDwfAnalogIOChannelNodeInfo(self.hdwf, idxChannel, idxNode)
        if result == 0:
            return None
        return self.TYPE(result)
    def channelNodeSetInfo(self, idxChannel, idxNode):
        return _l.FDwfAnalogIOChannelNodeSetInfo(self.hdwf, idxChannel, idxNode)
    def channelNodeSet(self, idxChannel, idxNode, value):
        _l.FDwfAnalogIOChannelNodeSet(self.hdwf, idxChannel, idxNode, value)
    def channelNodeGet(self, idxChannel, idxNode):
        return _l.FDwfAnalogIOChannelNodeGet(self.hdwf, idxChannel, idxNode)
    def channelNodeStatusInfo(self, idxChannel, idxNode):
        return _l.FDwfAnalogIOChannelNodeStatusInfo(
            self.hdwf, idxChannel, idxNode)
    def channelNodeStatus(self, idxChannel, idxNode):
        return _l.FDwfAnalogIOChannelNodeStatus(self.hdwf, idxChannel, idxNode)

# DIGITAL IO INSTRUMENT FUNCTIONS
class DwfDigitalIO(Dwf):
    '''Digital IO Intrumentation functions.

    Example:
    >>> dio = dwf.DwfDigitalIO()
    >>> dio.outputEnableSet(0xFF) # Enable DIO 0 -> 7
    >>> dio.outputSet(0x12)       # Set DIO pins high
    >>> dio.status()              # Retreive DIO status
    >>> hex(dio.inputStatus())
    0x12

    Args:
        idxDevice (int or dwf.Dwf): Device ID to use OR an instantiated DWF
            device. Default is '-1', which automatically selects the first
            device.
        idxCfg (int): Device Configuration to use. Default is None, which
            selects the default configuration. View what options are available
            for yout device in the Waveforms Device Configuration manager
    '''

    def __init__(self, idxDevice=-1, idxCfg=None):
        if isinstance(idxDevice, Dwf):
            self.hdwf = idxDevice.hdwf
        else:
            super(DwfDigitalIO, self).__init__(idxDevice, idxCfg)

    def reset(self, parent=False):
        ''' Reset all the DigitalIO instrument parameters to default values, set
        the output to zero (tri-state), and configures the DigitalIO instrument.

        Args:
            parent (bool): If True, use the Dwf Reset instead of the Digital IO
                reset. Default is False.
        '''
        if parent:
            super(DwfDigitalIO, self).reset()
        _l.FDwfDigitalIOReset(self.hdwf)

    def configure(self):
        '''Configure the DigitalIO instrument.

        Does not have to be called if the `AutoConfiguration` option is enabled.
        '''
        return _l.FDwfDigitalIOConfigure(self.hdwf)

    def status(self):
        '''Read the status and input values of the DigitalIO device to the PC.

        The status and values are accessed by the `inputStatus` method.
        '''
        _l.FDwfDigitalIOStatus(self.hdwf)

    def outputEnableInfo(self):
        '''Return the output enable mask that can be used on this device.

        These are the pins that can be used as outputs on this device.

        Returns:
            Available Device Output Pins as an int
        '''
        return _l.FDwfDigitalIOOutputEnableInfo(self.hdwf)

    def outputEnableSet(self, output_enable):
        '''Enable specific pins for output.

        This is used with `outputSet` to actually set the DIO output. This
        method enables the DIO pins to set, `outputSet` actually sets the logic
        level.

        Example:
        >>> dio = DwfDigitalIO()
        >>> dio.outputEnableSet(0xFF) # Enable DIO 0 -> 7
        >>> dio.outputSet(0x1F)       # Set DIO 0 -> 5 to High

        Args:
            output_enable (int): Integer mask for output pins.
        '''
        _l.FDwfDigitalIOOutputEnableSet(self.hdwf, output_enable)

    def outputEnableGet(self):
        '''Get the mask of enabled output pins.

        Returns:
            Integer mask of enabled output pins
        '''
        return _l.FDwfDigitalIOOutputEnableGet(self.hdwf)

    def outputInfo(self):
        '''
        Returns:
            The settable output value mask (bit set) that can be used on this device. 
        '''
        return _l.FDwfDigitalIOOutputInfo(self.hdwf)

    def outputSet(self, output):
        '''Set the output pins to the input value.

        This function works with `outputEnableSet`, where this function sets the
        logic level of the output pins, and `outputEnableSet` enables the output
        pins.

        Example:
        >>> dio = DwfDigitalIO()
        >>> dio.outputEnableSet(0xFF)   # Enable DIO 0 -> 7
        >>> dio.outputSet(0x07)         # Set DIO 0, 1, 2 to high

        Args:
            output (int): Bits to set high / low
        '''
        _l.FDwfDigitalIOOutputSet(self.hdwf, output)

    def outputGet(self):
        '''Get the output pin state set by `outputSet`.

        Returns:
            integer mask of output pins set high.
        '''
        return _l.FDwfDigitalIOOutputGet(self.hdwf)

    def inputInfo(self):
        '''Returns the readable input value mask (bit set) that can be used on the device.

        Returns:
            Integer mask of readable DigitIO pins.
        '''
        return _l.FDwfDigitalIOInputInfo(self.hdwf)

    def inputStatus(self):
        '''Return the input states of all I/O pins.

        Before calling the function above, call 'status' function to read the
        Digital I/O states from the device.

        Example:
        >>> dio = DwfDigitalDio()
        >>> dio.status()
        >>> dio.inputStatus()
        0x023
        '''
        return _l.FDwfDigitalIOInputStatus(self.hdwf)

# DIGITAL IN INSTRUMENT FUNCTIONS
class DwfDigitalIn(Dwf):
    '''Digital Input configuration / recording (Logic Analyzer).

    Configure Sample format and buffer size:
    >>> dev = dwf.DwfDigitalIn()
    >>> dev.sampleFormatSet(8)   # Bits
    >>> dev.buffserSizeSet(32)   # Bytes

    Configure Sample Rate:
    >>> dev.dividerSet(100)      # Divider set

    Acquire and wait:
    >>> dev.configure(False, True)
    >>> status = dev.status(True)
    >>> while status != dwf.Dwf.STATE.DONE:
    ...    time.sleep(0.5)
    ...    status = dev.status(True)
    ...

    Get results:
    >>> data = dev.statusData(32)

    Args:
        idxDevice (int): Device index to open. If set to '-1', the first found
            device will be used. Default is '-1'.
        idxCfg (int): Device configuration to use. The Device configuration can
            be found in the Waveforms GUI / Device Manager. Default is None (ie
            use the current configuration)
    '''
    class ACQMODE(IntEnum):
        '''Acquisition modes'''
        SINGLE          = _l.acqmodeSingle
        SCAN_SHIFT      = _l.acqmodeScanShift
        SCAN_SCREEN     = _l.acqmodeScanScreen
        RECORD          = _l.acqmodeRecord

    class CLOCKSOURCE(IntEnum):
        '''Digital In instrument clock sources.'''
        INTERNAL        = _l.DwfDigitalInClockSourceInternal
        EXTERNAL        = _l.DwfDigitalInClockSourceExternal

    class SAMPLEMODE(IntEnum):
        '''Sample acquisition mode.

        Simple is the default, an acquires one sample per period.

        Noise acquires one sample every few periods.

        # alternate samples: noise|sample|noise|sample|...
        # where noise is more than 1 transition between 2 samples
        '''
        SIMPLE          = _l.DwfDigitalInSampleModeSimple
        NOISE           = _l.DwfDigitalInSampleModeNoise

    def __init__(self, idxDevice=-1, idxCfg=None):
        if isinstance(idxDevice, Dwf):
            self.hdwf = idxDevice.hdwf
        else:
            super(DwfDigitalIn, self).__init__(idxDevice, idxCfg)

    def reset(self, parent=False):
        ''' Reset all the DigitalIn instrument parameters to default values, set
        the output to zero (tri-state), and configures the DigitalIn instrument.

        Args:
            parent (bool): If True, use the Dwf Reset instead of the Digital IO
                reset. Default is False.
        '''
        if parent:
            super(DwfDigitalIn, self).reset()
        _l.FDwfDigitalInReset(self.hdwf)

    def configure(self, reconfigure, start):
        '''Configure the device and stop / stop the the acquisition.

        To reset the Auto trigger timeout, set reconfigure to True.

        Args:
            reconfigure (bool): Configure the device.
            start (bool): Start the acquisition.
        '''
        return _l.FDwfDigitalInConfigure(self.hdwf, reconfigure, start)
    def status(self, read_data=False):
        '''Check the instrument state, and / or read device data.

        Args:
            read_data (bool): If True, read data from the device. Default is
                False.

        Returns:
            instrument state (dwf.DwfDigitalIn.STATE) enumerated type
        '''
        return self.STATE(_l.FDwfDigitalInStatus(self.hdwf, read_data))

    def statusSamplesLeft(self):
        '''Retreive the number of samples remaining in the acquisition.

        Returns:
            Number of samples left (as an integer)
        '''
        return _l.FDwfDigitalInStatusSamplesLeft(self.hdwf)

    def statusSamplesValid(self):
        '''Retreive the number of valid / acquired data samples.

        Returns:
            Number of samples acquired (as an integer)
        '''
        return _l.FDwfDigitalInStatusSamplesValid(self.hdwf)

    def statusIndexWrite(self):
        '''Retreive the buffer write pointer, which is needed when using the
        Scan Screen acquisition mode to display the scan bar.

        Returns:
            Buffer write pointer index (as an integer)
        '''
        return _l.FDwfDigitalInStatusIndexWrite(self.hdwf)

    def statusAutoTriggered(self):
        '''Is the acquisition configured for Auto trigger?

        Returns:
            True if the acquisition is configured for Auto trigger. False
            otherwise
        '''
        return bool(_l.FDwfDigitalInStatusAutoTriggered(self.hdwf))

    def statusData(self, count):
        '''Acquire sample data from the instrument.

        The sample format is specified by sampleFormatSet method.

        Args:
            count (int): Number of samples to copy

        Returns:
            Retreived data in the set format (list of integers)
        '''
        bit_width = self.sampleFormatGet()
        countOfDataBytes = count * (bit_width // 8)
        data = _l.FDwfDigitalInStatusData(self.hdwf, countOfDataBytes)

        if bit_width == 16:
            data = [  (data[2*i+1] & 0xff) << 8
                    | (data[2*i] & 0xff)
                    for i in range(len(data) // 2)]
        elif bit_width == 32:
            data = [  ((data[4*i+3] & 0xff) << 24)
                    | ((data[4*i+2] & 0xff) << 16)
                    | ((data[4*i+1] & 0xff) << 8)
                    | (data[4*i] & 0xff)
                     for i in range(len(data) // 4)]

        return data

    def statusRecord(self):
        '''Get the number of samples available, lost, or corrupted.

        Returns:
            Tuple of integers (Available, Lost, Corrupted)
        '''
        return _l.FDwfDigitalInStatusRecord(self.hdwf)

    def internalClockInfo(self):
        '''Get the internal clock frequency.

        Returns:
            Internal Clock Frequency (as an integer)
        '''
        return _l.FDwfDigitalInInternalClockInfo(self.hdwf)

    def clockSourceInfo(self):
        '''Find the supported clock sources for the Digital In isntrument.

        Returns:
            A set of device supported clocks (dwf.DwfDigitalIn.CLOCKSOURCE)
        '''
        return _make_set(
            _l.FDwfDigitalInClockSourceInfo(self.hdwf), self.CLOCKSOURCE)

    def clockSourceSet(self, clock_source):
        '''Set the clock source to the selected clock.

        Args:
            clock_source (dwf.DwfDigitalIn.CLOCKSOURCE): Clock source to use.
                Options are:
                - CLOCKSOURCE.INTERNAL
                - CLOCKSOURCE.EXTERNAL
        '''
        _l.FDwfDigitalInClockSourceSet(self.hdwf, clock_source)

    def clockSourceGet(self):
        '''Get the currently set clock source.

        Returns:
            dwf.DwfDigitalIn.CLOCKSOURCE
        '''
        return self.CLOCKSOURCE(_l.FDwfDigitalInClockSourceGet(self.hdwf))

    def dividerInfo(self):
        '''Get the instrument's maximum supported clock divider (determines the
        sample rate.

        Returns:
            Maximum Divider as an integer.
        '''
        return _l.FDwfDigitalInDividerInfo(self.hdwf)

    def dividerSet(self, div):
        '''Set the instrument's clock divider.

        Args:
            div (int): Clock divider.
        '''
        _l.FDwfDigitalInDividerSet(self.hdwf, div)

    def dividerGet(self):
        '''Get the currently set clock divider.

        Returns:
            Clock divider as an integer.
        '''
        return _l.FDwfDigitalInDividerGet(self.hdwf)

    def bitsInfo(self):
        '''Get the instruments bit format.

        Returns:
            The number of Digital In bits (8, 16, 32)
        '''
        return _l.FDwfDigitalInBitsInfo(self.hdwf)

    def sampleFormatSet(self, bits):
        '''Set the instrument bit format.

        Args:
            bits (int): Bit format. Valid options are:
                - 8
                - 16
                - 32
        '''
        _l.FDwfDigitalInSampleFormatSet(self.hdwf, bits)

    def sampleFormatGet(self):
        '''Get the instrument's bit format.

        Returns:
            Bit format as an integer (8, 16, 32)
        '''
        return _l.FDwfDigitalInSampleFormatGet(self.hdwf)

    def bufferSizeInfo(self):
        '''Get the Maximum buffer size for the Digital In Instrument.

        Returns:
            Maximum buffer size as an integer (in bytes?)
        '''
        return _l.FDwfDigitalInBufferSizeInfo(self.hdwf)

    def bufferSizeSet(self, size):
        '''Set the instrument's buffer size.

        Args:
            size (int) Buffer size (in Bytes?)
        '''
        _l.FDwfDigitalInBufferSizeSet(self.hdwf, size)

    def bufferSizeGet(self):
        '''Get the instrument's buffer size.

        Returns:
            Buffer size as an integer (in Bytes?)
        '''
        return _l.FDwfDigitalInBufferSizeGet(self.hdwf)

    def sampleModeInfo(self):
        '''Get the support sample modes of the instrument.

        Sample modes are:

        - dwf.DwfDigitalIn.SAMPLEMODE.SIMPLE = store one sample on every clock
          divider pulse
        - dwf.DwfDigitalIn.SAMPLEMODE.NOISE = store alternating noise and sample
          values, where noise is more than one transition between two samples.
          (available when clock divider > 1)

        Returns:
            Supported sample modes as a set of enums
        '''
        return _make_set(
            _l.FDwfDigitalInSampleModeInfo(self.hdwf), self.SAMPLEMODE)

    def sampleModeSet(self, sample_mode):
        '''Set the instrument's sample mode.

        Args:
            sample_mode (dwf.DwfDigitalIn.SAMPLEMODE): SIMPLE or NOISE.
        '''
        _l.FDwfDigitalInSampleModeSet(self.hdwf, sample_mode)

    def sampleModeGet(self):
        '''Get the instrument's sample mode.

        Returns:
            dwf.DwfDigitalIn.SAMPLEMODE (SIMPLE or NOISE)
        '''
        return self.SAMPLEMODE(_l.FDwfDigitalInSampleModeGet(self.hdwf))

    def acquisitionModeInfo(self):
        '''Get the instrument's supported acquisition modes.

        The valid acquisition modes are:

        - dwf.DwfDigitalIn.ACQMODE.SINGLE = Perform a single buffer acquisition

        - dwf.DwfDigitalIn.ACQMODE.SCANSHIFT = Perform a continuous scan in a
          FIFO style. The trigger setting is ignored.

        - dwf.DwfDigitalIn.ACQMODE.SCANSCREEN = Perform a continuous acquisition
          circularly writing samples into the buffer. The trigger setting is
          ignored.

        Returns:
            dwf.DwfDigitalIn.ACQMODE settings as a frozen set (SINGLE,
            SCANSHIFT, SCANSCREEN)
        '''
        return _make_set(
            _l.FDwfDigitalInAcquisitionModeInfo(self.hdwf), self.ACQMODE)

    def acquisitionModeSet(self, acqmode):
        '''Set the acquisition mode.

        Args:
            acqmode (dwf.DwfDigitalIn.ACQMODE): Acquisition mode (SINGLE,
            SCANSCREEN, SCANSHIFT)
        '''
        _l.FDwfDigitalInAcquisitionModeSet(self.hdwf, acqmode)

    def acquisitionModeGet(self):
        '''Get the currently set acquisition mode.

        Returns:
            dwf.DwfDigtialIn.ACQMODE set (SINGLE, SCANSCREEN, or SCANSHIFT)
        '''
        return self.ACQMODE(_l.FDwfDigitalInAcquisitionModeGet(self.hdwf))

    def triggerSourceInfo(self):
        '''Supported trigger options for the DwfDigitalIn instrument.

        Returns:
            Available triggers for this instrument (dwf.Dwf.TRIGSRC)
        '''
        return _make_set(
            _l.FDwfDigitalInTriggerSourceInfo(self.hdwf), self.TRIGSRC)

    def triggerSourceSet(self, trigsrc):
        '''Set the instrument trigger source.

        Args:
            trigsrc (dwf.Dwf.TRIGSRC): Trigger source to use.
        '''
        _l.FDwfDigitalInTriggerSourceSet(self.hdwf, trigsrc)

    def triggerSourceGet(self):
        '''Get the currently set instrument trigger source.

        Returns:
            Set trigger source as an enum (dwf.Dwf.TRIGSRC)
        '''
        return self.TRIGSRC(_l.FDwfDigitalInTriggerSourceGet(self.hdwf))

    def triggerPositionInfo(self):
        '''Get the maximum value for the trigger position in samples.

        This can be greater than the buffer size.

        Returns:
            Maximum trigger position in samples as an integer.
        '''
        return _l.FDwfDigitalInTriggerPositionInfo(self.hdwf)

    def triggerPositionSet(self, samples_after_trigger):
        '''Set the trigger position in samples.

        Args:
            samples_after_trigger (int): Number of samples to wait after the
                trigger to start acquiring.
        '''
        _l.FDwfDigitalInTriggerPositionSet(self.hdwf, samples_after_trigger)

    def triggerPositionGet(self):
        '''Get the currently set trigger position.

        Returns:
            Number of samples to wait after trigger to acquire.
        '''
        return _l.FDwfDigitalInTriggerPositionGet(self.hdwf)

    def triggerAutoTimeoutInfo(self):
        '''Get the minimum and maximum auto trigger timeout values, as well as
        the number of adjustable steps.

        The acquisition is autotriggered when the specified time elapses.

        When this is set to '0' the timeout is disabled, and the acquisition
        proceeds as normal.

        Returns:
            (Min, Max, Step) auto trigger timeout values in seconds
        '''
        return _l.FDwfDigitalInTriggerAutoTimeoutInfo(self.hdwf)

    def triggerAutoTimeoutSet(self, secTimeout):
        '''Set the Auto trigger timeout.

        The acquisition is autotriggered when the specified time elapses.

        When this is set to '0' the timeout is disabled, and the acquisition
        proceeds as normal.

        Args:
            secTimeout (int): Timeout as a float in seconds.
        '''
        _l.FDwfDigitalInTriggerAutoTimeoutSet(self.hdwf, secTimeout)

    def triggerAutoTimeoutGet(self):
        '''Get the instruments auto trigger timeout.

        Returns:
            Auto trigger timeout as a float in seconds.
        '''
        return _l.FDwfDigitalInTriggerAutoTimeoutGet(self.hdwf)

    def triggerInfo(self):
        '''Get the device supported instrument triggers.

        Each bit of each returned integer represents a Digital In pin. Each pins
        can support one of the four trigger types:

        - Trigger on Low Logic Level
        - Trigger on High Logic Level
        - Trigger on Rising Edge
        - Trigger on Falling Edge

        Returns:
            Four integers (Level Low, Level High, Rising Edge, Falling Edge).
        '''
        return _l.FDwfDigitalInTriggerInfo(self.hdwf)

    def triggerSet(self, level_low, level_high, edge_rise, edge_fall):
        '''Configure the Digital Trigger detector for each DigitalIn pin.

        Configure DIO 0 for Either Edge:
        >>> dev = dwf.DwfDigitalIn()
        >>> dev.triggerSet(0x00, 0x00, 0x01, 0x01)

        Configure DIO 1 for Logic Level Low:
        >>> dev = dwf.DwfDigitalIn()
        >>> dev.triggerSet(0x02, 0x00, 0x00, 0x00)

        Configure DIO0 for Low, DIO1 for High, DIO2 for Rising, DIO3
        for falling:
        >>> dev = dwf.DwfDigitalIn()
        >>> dev.triggerSet(0x01, 0x02, 0x04, 0x08)

        Args:
            level_low (int): Pins to trigger on logic level low
            level_high (int): Pins to trigger on logic level high
            edge_rise (int): Pins to trigger on a rising edge
            edge_fall (int): Pins to trigger on a falling edge
        '''
        _l.FDwfDigitalInTriggerSet(self.hdwf, level_low, level_high, edge_rise, edge_fall)

    def triggerGet(self):
        '''Get the instrument's configured digital trigger.

        Each integer's bit represents a Digital In Pin, for one of the triggers.

        Returns:
            Tuple of configured triggers (Logic Level Low, Logic Level High,
            Rising Edge, Falling Edge)
        '''
        return _l.FDwfDigitalInTriggerGet(self.hdwf)

class DwfDigitalOut(Dwf):
    '''Digital Pattern generation instrument controls / functionality.

    Example:
    >>> dev = dwf.DwfDigitalOut()

    Args:
        idxDevice (int): Device index to open. If set to '-1', the first found
            device will be used. Default is '-1'.
        idxCfg (int): Device configuration to use. The Device configuration can
            be found in the Waveforms GUI / Device Manager. Default is None (ie
            use the current configuration)
    '''

    class OUTPUT(IntEnum):
        PUSH_PULL           = _l.DwfDigitalOutOutputPushPull
        OPEN_DRAIN          = _l.DwfDigitalOutOutputOpenDrain
        OPEN_SOURCE         = _l.DwfDigitalOutOutputOpenSource
        TRISTATE            = _l.DwfDigitalOutOutputThreeState # for custom and random

    class TYPE(IntEnum):
        PULSE               = _l.DwfDigitalOutTypePulse
        CUSTOM              = _l.DwfDigitalOutTypeCustom
        RANDOM              = _l.DwfDigitalOutTypeRandom

    class IDLE(IntEnum):
        INIT                = _l.DwfDigitalOutIdleInit
        LOW                 = _l.DwfDigitalOutIdleLow
        HIGH                = _l.DwfDigitalOutIdleHigh
        HiZ                 = _l.DwfDigitalOutIdleZet

    def __init__(self, idxDevice=-1, idxCfg=None):
        if isinstance(idxDevice, Dwf):
            self.hdwf = idxDevice.hdwf
        else:
            super(DwfDigitalOut, self).__init__(idxDevice, idxCfg)

    def reset(self, parent=False):
        ''' Reset all the DigitalOut instrument parameters to default values,
        set the output to zero (tri-state), and configures the DigitalOut
        instrument.

        Args:
            parent (bool): If True, use the Dwf Reset instead of the Digital IO
                reset. Default is False.
        '''
        if parent:
            super(DwfDigitalOut, self).reset()
        return _l.FDwfDigitalOutReset(self.hdwf)

    def configure(self, start):
        '''Start or stop the pattern generation.

        Args:
            start (bool): If True, start pattern generation. If False, stop the
                pattern generation.
        '''
        _l.FDwfDigitalOutConfigure(self.hdwf, start)

    def status(self):
        '''Get the current state of the instrument.

        Returns:
            Instrument state as an enum (dwf.Dwf.STATE)
        '''
        return self.STATE(_l.FDwfDigitalOutStatus(self.hdwf))

    def internalClockInfo(self):
        '''Get the instruments internal clock frequency.

        Returns:
            Internal clock frequency as an integer.
        '''
        return _l.FDwfDigitalOutInternalClockInfo(self.hdwf)

    def triggerSourceInfo(self):
        '''List the supported trigger source options for the instument.

        Returns:
            Frozen set of supported Trigger sources (dwf.Dwf.TRIGSRC)
        '''
        return _make_set(
            _l.FDwfDigitalOutTriggerSourceInfo(self.hdwf), self.TRIGSRC)

    def triggerSourceSet(self, trigsrc):
        '''Set the instrument trigger source.

        Args:
            trigsrc (dwf.Dwf.TRIGSRC): Trigger source to start pattern
                generation.
        '''
        _l.FDwfDigitalOutTriggerSourceSet(self.hdwf, trigsrc)

    def triggerSourceGet(self):
        '''Get the instrument trigger source.

        Returns:
            The set trigger source (dwf.Dwf.TRIGSRC)
        '''
        return self.TRIGSRC(_l.FDwfDigitalOutTriggerSourceGet(self.hdwf))

    def runInfo(self):
        '''Get the supported run length of the instrument in seconds.

        Non zero values represent valid possible run lengths for the DigialOut
        instrument.

        A value of '0' represents continuous mode.

        Returns:
            (Min, Max) Run length in seconds (float)
        '''
        return _l.FDwfDigitalOutRunInfo(self.hdwf)

    def runSet(self, secRun):
        '''Set the run time of the instrument.

        Args:
            secRun (float): Run time in seconds as a float. If 0, the outptu
                will be configured for continuous mode.
        '''
        _l.FDwfDigitalOutRunSet(self.hdwf, secRun)

    def runGet(self):
        '''Get the configured instrument run time.

        Returns:
            Instrument run time as a float. Note: a value of '0' means
            continuous mode.
        '''
        return _l.FDwfDigitalOutRunGet(self.hdwf)

    def runStatus(self):
        '''Get the remaining time for the instrument from the current pattern
        generation.

        Returns:
            Remaining run time as a float.
        '''
        return _l.FDwfDigitalOutRunStatus(self.hdwf)

    def waitInfo(self):
        '''Get information about the after trigger wait time for the instrument.

        When a trigger event occurs, the instrument will wait an amount of time
        before pattern generation. The wait time here is that time.

        Returns:
            (Min, Max) wait time in seconds as a float.
        '''
        return _l.FDwfDigitalOutWaitInfo(self.hdwf)

    def waitSet(self, secWait):
        '''Set the after trigger wait time for the instrument.

        Args:
            secWait (float): After trigger wait time in seconds
        '''
        _l.FDwfDigitalOutWaitSet(self.hdwf, secWait)

    def waitGet(self):
        '''Get the configured trigger wait time for the instrument.

        Returns:
            After trigger wait time in second.
        '''
        return _l.FDwfDigitalOutWaitGet(self.hdwf)

    def repeatInfo(self):
        '''Get the supported repeat count range, which is how many times the
        generated signal will be repeated.

        '0' here mean repeating forever.

        Returns:
            (Min, Max) repeat count as a tuple
        '''
        return _l.FDwfDigitalOutRepeatInfo(self.hdwf)

    def repeatSet(self, repeat):
        '''Set the number of times to repeat the generated signal.

        Args:
            repeat (int): Number of times to repeat the sigal. A value of '0'
                means repeat the signal forever.
        '''
        _l.FDwfDigitalOutRepeatSet(self.hdwf, repeat)

    def repeatGet(self):
        '''Get the number of times the generated signal is set to repeat for.

        Returns:
            Number of times the generated signal will repeat (as an integer)
        '''
        return _l.FDwfDigitalOutRepeatGet(self.hdwf)

    def repeatStatus(self):
        '''Get the remaining number of counts left in the generation output.

        This does not retreive data from the device. This method uses the
        information retreived from `dev.status`, so that must be called before
        this method will return meaningful results.

        Returns:
            Remaining number of generation cycles as an integer.
        '''
        return _l.FDwfDigitalOutRepeatStatus(self.hdwf)

    def repeatTriggerSet(self, repeat_trigger):
        '''Include or exclude the wait / run repeat cycles.

        Args:
            repeat_trigger (bool): If true, include in the wait / run repeat
                cycle.
        '''
        _l.FDwfDigitalOutRepeatTriggerSet(self.hdwf, repeat_trigger)

    def repeatTriggerGet(self):
        '''Get the repeat trigger inclusion / exclusion setting from the
        instrument.

        Returns:
            True if included in the wait - run repeat cycle. False otherwise.
        '''
        return bool(_l.FDwfDigitalOutRepeatTriggerGet(self.hdwf))

    def channelCount(self): #renamed
        '''Get the number of Digital Out channels of the device's instrument.

        Returns:
            Number of digital out channels as an integer.
        '''
        return _l.FDwfDigitalOutCount(self.hdwf)

    def enableSet(self, idxChannel, enable):
        '''Set the input channels enable state.

        Args:
            idxChannel (int): DigitalOut Channel index.
            enable (bool): Enable (True) or disable (False) the selected
                Channel.
        '''
        _l.FDwfDigitalOutEnableSet(self.hdwf, idxChannel, enable)

    def enableGet(self, idxChannel):
        '''Get the selected channels enabled state.

        Returns:
            True if enabled, false otherwise.
        '''
        return bool(_l.FDwfDigitalOutEnableGet(self.hdwf, idxChannel))

    def outputInfo(self, idxChannel):
        '''Get the selected channels valid output states.

        Depending on the selected channel, the following output states (dwf.DwfDigitalOut.OUTPUT) are available:

        - dwf.DwfDigitalOut.OUTPUT.PUSH_PULL
        - dwf.DwfDigitalOut.OUTPUT.OPEN_DRAIN
        - dwf.DwfDigitalOut.OUTPUT.OPEN_SOURCE
        - dwf.DwfDigitalOut.OUTPUT.TRISTATE

        The `OPEN_DRAIN` and `OPEN_SOURCE` types require External Pullup or pull
        down resistors.

        The `TRISTATE` type is available when using the `custom` or `random`
        types?

        Returns:
            Tuple of valid channel states (dwf.DwfDigitalOut.OUTPUT)
        '''
        return _make_set(
            _l.FDwfDigitalOutOutputInfo(self.hdwf, idxChannel), self.OUTPUT)

    def outputSet(self, idxChannel, output_mode):
        '''Set the selected channels output Type.

        Depending on the selected channel, the following output states (dwf.DwfDigitalOut.OUTPUT) are available:

        - dwf.DwfDigitalOut.OUTPUT.PUSH_PULL
        - dwf.DwfDigitalOut.OUTPUT.OPEN_DRAIN
        - dwf.DwfDigitalOut.OUTPUT.OPEN_SOURCE
        - dwf.DwfDigitalOut.OUTPUT.TRISTATE

        The `OPEN_DRAIN` and `OPEN_SOURCE` types require External Pullup or pull
        down resistors.

        The `TRISTATE` type is available when using the `custom` or `random`
        types?

        Args:
            idxChannel (int): Digital Output channel index
            output_mode (dwf.DwfDigitalOut): Output type
        '''
        _l.FDwfDigitalOutOutputSet(self.hdwf, idxChannel, output_mode)

    def outputGet(self, idxChannel):
        '''Get the channel output type.

        Args:
            idxChannel (int): Digital Output channel index

        Returns:
            Input channel's output type (dwf.DwfDigitalOut)
        '''
        return self.OUTPUT(_l.FDwfDigitalOutOutputGet(self.hdwf, idxChannel))

    def typeInfo(self, idxChannel):
        '''Get the input channel's supported type.

        The Channel types are:

        - dwf.DwfDigitalOut.TYPE.PULSE
        - dwf.DwfDigitalOut.TYPE.CUSTOM
        - dwf.DwfDigitalOut.TYPE.RANDOM

        Args:
            idxChannel (int): Digital Output channel index

        Returns:
            Input channel's supported types as a frozen set of enums.
        '''
        return _make_set(
            _l.FDwfDigitalOutTypeInfo(self.hdwf, idxChannel), self.TYPE)

    def typeSet(self, idxChannel, output_type):
        '''Set the input channel's type.

        The Channel output modes are:

        - dwf.DwfDigitalOut.TYPE.PULSE
        - dwf.DwfDigitalOut.TYPE.CUSTOM
        - dwf.DwfDigitalOut.TYPE.RANDOM

        Args:
            idxChannel (int): Digital Output channel index
        '''
        _l.FDwfDigitalOutTypeSet(self.hdwf, idxChannel, output_type)

    def typeGet(self, idxChannel):
        '''Get the set channel type.

        Args:
            idxChannel (int): Digital Output channel index

        Returns:
            The selected channel's type as an dwf.DwfDigitalOut.TYPE enum
        '''
        return self.TYPE(_l.FDwfDigitalOutTypeGet(self.hdwf, idxChannel))

    def idleInfo(self, idxChannel):
        '''Get the selected channel idle output states available.

        Idle states are:

        - dwf.DwfDigitalOut.IDLE.INIT
        - dwf.DwfDigitalOut.IDLE.LOW
        - dwf.DwfDigitalOut.IDLE.HIGH
        - dwf.DwfDigitalOut.IDLE.HiZ

        Args:
            idxChannel (int): Selected channel

        Returns:
            Frozen set of input channel's idle output states.
        '''
        return _make_set(
            _l.FDwfDigitalOutIdleInfo(self.hdwf, idxChannel), self.IDLE)

    def idleSet(self, idxChannel, idle_mode):
        '''Set the selected channel's output in the Idle state.

        Idle states are:

        - dwf.DwfDigitalOut.IDLE.INIT
        - dwf.DwfDigitalOut.IDLE.LOW
        - dwf.DwfDigitalOut.IDLE.HIGH
        - dwf.DwfDigitalOut.IDLE.HiZ

        Args:
            idxChannel (int): Selected output channel
            idle_mode (dwf.DwfDigitalOut.IDLE): Output IDLE mode.
        '''
        _l.FDwfDigitalOutIdleSet(self.hdwf, idxChannel, idle_mode)

    def idleGet(self, idxChannel):
        '''Get the selected channel's set Idle state.

        Args:
            idxChannel (int): Selected output channel

        Returns:
            Selected channel's idle output state as an enum (dwf.DwfDigitalOut.IDLE)
        '''
        return self.IDLE(_l.FDwfDigitalOutIdleGet(self.hdwf, idxChannel))

    def dividerInfo(self, idxChannel):
        '''Get the minimum and maximum supported clock divider for the selected
        digital out channel.

        Args:
            idxChannel (int): Selected Digital Out Channel

        Returns:
            (Min, Max) channel clock divider.
        '''
        return _l.FDwfDigitalOutDividerInfo(self.hdwf, idxChannel)

    def dividerInitSet(self, idxChannel, init):
        '''Set the initial clock divider for the selected channel.

        Args:
            idxChannel (int): Selected Digital Out Channel
            init (int): Clock Divider
        '''
        _l.FDwfDigitalOutDividerInitSet(self.hdwf, idxChannel, init)

    def dividerInitGet(self, idxChannel):
        '''Get the initial clock divider for the selected channel.

        Args:
            idxChannel (int): Selected Digital Out Channel

        Returns:
            Set initial clock divider as an integer.
        '''
        return _l.FDwfDigitalOutDividerInitGet(self.hdwf, idxChannel)

    def dividerSet(self, idxChannel, value):
        '''Set the running mode clock divider for the selected channel.

        Args:
            idxChannel (int): Selected Digital Out Channel
            value (int): Clock Divider
        '''
        _l.FDwfDigitalOutDividerSet(self.hdwf, idxChannel, value)

    def dividerGet(self, idxChannel):
        '''Get the clock divider for the selected channel.

        Args:
            idxChannel (int): Selected Digital Out Channel

        Returns:
            Clock divider as an integer.
        '''
        return _l.FDwfDigitalOutDividerGet(self.hdwf, idxChannel)

    def counterInfo(self, idxChannel):
        '''Get the channel's supported counter range.

        Args:
            idxChannel (int): Selected Digital Out Channel

        Returns:
            (Min, Max) counter range as an integer.
        '''
        return _l.FDwfDigitalOutCounterInfo(self.hdwf, idxChannel)

    def counterInitSet(self, idxChannel, start_high, init):
        '''Set the channel's initial counter value and state.

        Args:
            idxChannel (int): Selected Digital Out Channel
            start_high (bool): Initial counter state. True is enabled.
            init (int): Intial counter value.
        '''
        _l.FDwfDigitalOutCounterInitSet(self.hdwf, idxChannel, start_high, init)

    def counterInitGet(self, idxChannel):
        '''Get the channel's inital counter value and state.

        Args:
            idxChannel (int): Selected Digital Out Channel

        Returns:
            (State <bool>, Counter Value <int>)
        '''
        return _l.FDwfDigitalOutCounterInitGet(self.hdwf, idxChannel)

    def counterSet(self, idxChannel, low, high):
        '''Set the channel's low and high counter value.

        Args:
            idxChannel (int): Selected Digital Out Channel
            low (int): Counter low value
            high (int): Counter high value
        '''
        _l.FDwfDigitalOutCounterSet(self.hdwf, idxChannel, low, high)

    def counterGet(self, idxChannel):
        '''Get the channel's low / high counter value.

        Args:
            idxChannel (int): Selected Digital Out Channel

        Returns:
            (Low, High) counter values as integers
        '''
        return _l.FDwfDigitalOutCounterGet(self.hdwf, idxChannel)

    def dataInfo(self, idxChannel):
        '''Get the maximum buffer size for the number of customer data bits.

        Args:
            idxChannel (int): Selected Digital Out Channel

        Returns:
            Maximum buffer size in bytes.
        '''
        return _l.FDwfDigitalOutDataInfo(self.hdwf, idxChannel)

    def dataSet(self, idxChannel, rgBits):
        '''Configure the custom data output.

        The data is sent out through the selected channel in LSB order. Each
        output is configured using two bits:

        - Bit 0 (2, 4, 6, etc.) Output Value
        - Bit 1 (3, 5, 7, etc.) Output Enable

        This function also sets the Counter initial, low, and high values,
        according to the number of bits.

        I'm not 100% sure how this works, more information is needed.

        Args:
            idxChannel (int): Selected Digital Out Channel
            rgBits (list): Array of bits / bytes to be sent.
        '''
        _l.FDwfDigitalOutDataSet(self.hdwf, idxChannel, rgBits)
