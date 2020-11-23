
import unittest.mock

import pytest

import dwf

def test_init_default():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            low_level_patch.FDwfDeviceOpen.assert_called_once_with(-1)
            hdwf_patch.assert_called_once_with(low_level_patch.FDwfDeviceOpen.return_value)

@pytest.mark.parametrize('device_id', [-1, 0, 100])
def test_init_device_id(device_id):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn(device_id)

            low_level_patch.FDwfDeviceOpen.assert_called_once_with(device_id)
            hdwf_patch.assert_called_once_with(low_level_patch.FDwfDeviceOpen.return_value)

@pytest.mark.parametrize('device_id', [-1, 0, 100])
@pytest.mark.parametrize('device_cfg', [0, 100])
def test_init_device_id_and_device_config(device_id, device_cfg):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn(device_id, device_cfg)

            low_level_patch.FDwfDeviceConfigOpen.assert_called_once_with(device_id, device_cfg)
            hdwf_patch.assert_called_once_with(low_level_patch.FDwfDeviceConfigOpen.return_value)

def test_init_none():
    with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
        low_level_patch.FDwfDeviceOpen.return_value = dwf.Dwf.DEVICE_NONE

        with pytest.raises(RuntimeError):
            dwf.DwfDigitalIn()

def test_init_dwf():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.Dwf()
            digital_dev = dwf.DwfDigitalIn(dev)

            low_level_patch.FDwfDeviceOpen.assert_called_once_with(-1)
            hdwf_patch.assert_called_once_with(low_level_patch.FDwfDeviceOpen.return_value)

def test_digital_in_reset():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()
            dev.reset()

            low_level_patch.FDwfDigitalInReset.assert_called_once_with(dev.hdwf)

def test_device_in_reset():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()
            dev.reset(parent=True)

            low_level_patch.FDwfDeviceReset.assert_called_once_with(dev.hdwf)

@pytest.mark.parametrize('reconfigure', [True, False])
@pytest.mark.parametrize('start', [True, False])
def test_configure(start, reconfigure):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            dev.configure(reconfigure, start)

            low_level_patch.FDwfDigitalInConfigure.assert_called_once_with(dev.hdwf, reconfigure, start)

@pytest.mark.parametrize('read', [True, False])
@pytest.mark.parametrize('state', dwf.DwfDigitalIn.STATE)
def test_status(read, state):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            low_level_patch.FDwfDigitalInStatus.return_value = state

            value = dev.status(read)

            assert value == state
            low_level_patch.FDwfDigitalInStatus.assert_called_once_with(dev.hdwf,
                    read)

def test_status_samples_left():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            value = dev.statusSamplesLeft()

            low_level_patch.FDwfDigitalInStatusSamplesLeft.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalInStatusSamplesLeft.return_value

def test_status_samples_valid():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            value = dev.statusSamplesValid()

            low_level_patch.FDwfDigitalInStatusSamplesValid.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalInStatusSamplesValid.return_value

def test_status_index_write():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            value = dev.statusIndexWrite()

            low_level_patch.FDwfDigitalInStatusIndexWrite.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalInStatusIndexWrite.return_value

@pytest.mark.parametrize("return_value", [True, False])
def test_status_auto_triggered(return_value):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            low_level_patch.FDwfDigitalInStatusAutoTriggered.return_value = return_value
            dev = dwf.DwfDigitalIn()

            value = dev.statusAutoTriggered()

            low_level_patch.FDwfDigitalInStatusAutoTriggered.assert_called_once_with(dev.hdwf)
            assert value == return_value

EXPECTED = [
    # Sample Format, Samples, Data,                         Expected
    (16,             1,       [0xFF, 0x00],                 [0x00FF]),
    (16,             1,       [0x00, 0xFF],                 [0xFF00]),
    (16,             1,       [0xF0, 0x0F],                 [0x0FF0]),
    (16,             2,       [0x00, 0xFF, 0xFF, 0x00],     [0xFF00, 0x00FF]),

    (32,             1,       [0xFF, 0x00, 0x00, 0x00],     [0x000000FF]),
    (32,             1,       [0x00, 0x00, 0x00, 0xFF],     [0xFF000000]),
]

@pytest.mark.parametrize('sample_format,samples,data,expected', EXPECTED)
def test_status_data(sample_format, samples, data, expected):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            low_level_patch.FDwfDigitalInSampleFormatGet.return_value = sample_format
            low_level_patch.FDwfDigitalInStatusData.return_value = data

            value = dev.statusData(samples)

            assert value == expected
            low_level_patch.FDwfDigitalInStatusData.assert_called_once()

def test_status_record():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            value = dev.statusRecord()

            low_level_patch.FDwfDigitalInStatusRecord.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalInStatusRecord.return_value

def test_internal_clock_info():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            value = dev.internalClockInfo()

            low_level_patch.FDwfDigitalInInternalClockInfo.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalInInternalClockInfo.return_value

@pytest.mark.parametrize('clock', dwf.DwfDigitalIn.CLOCKSOURCE)
def test_clock_source_info(clock):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            low_level_patch.FDwflDigitalInClockSourceInfo.return_value = clock
            value = dev.clockSourceInfo()

            low_level_patch.FDwfDigitalInClockSourceInfo.assert_called_once_with(dev.hdwf)

@pytest.mark.parametrize('clock', dwf.DwfDigitalIn.CLOCKSOURCE)
def test_clock_source_set(clock):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            dev.clockSourceSet(clock)

            low_level_patch.FDwfDigitalInClockSourceSet.assert_called_once_with(dev.hdwf, clock)

@pytest.mark.parametrize('clock', dwf.DwfDigitalIn.CLOCKSOURCE)
def test_clock_source_get(clock):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()
            low_level_patch.FDwfDigitalInClockSourceGet.return_value = clock

            value = dev.clockSourceGet()

            low_level_patch.FDwfDigitalInClockSourceGet.assert_called_once_with(dev.hdwf)
            assert value == clock

def test_divider_info():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            value = dev.dividerInfo()

            low_level_patch.FDwfDigitalInDividerInfo.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalInDividerInfo.return_value

@pytest.mark.parametrize('divider', [1, 10])
def test_divider_set(divider):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()
            dev.dividerSet(divider)

            low_level_patch.FDwfDigitalInDividerSet.assert_called_once_with(dev.hdwf, divider)

def test_divider_get():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            value = dev.dividerGet()

            low_level_patch.FDwfDigitalInDividerGet.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalInDividerGet.return_value

def test_bits_info():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            value = dev.bitsInfo()

            low_level_patch.FDwfDigitalInBitsInfo.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalInBitsInfo.return_value

@pytest.mark.parametrize('bits', [8, 16, 32])
def test_sample_format_set(bits):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            dev.sampleFormatSet(bits)

            low_level_patch.FDwfDigitalInSampleFormatSet.assert_called_once_with(dev.hdwf, bits)

def test_sample_format_get():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            value = dev.sampleFormatGet()

            low_level_patch.FDwfDigitalInSampleFormatGet.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalInSampleFormatGet.return_value

def test_buffer_size_info():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            value = dev.bufferSizeInfo()

            low_level_patch.FDwfDigitalInBufferSizeInfo.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalInBufferSizeInfo.return_value

@pytest.mark.parametrize('size', [0, 100])
def test_buffer_size_set(size):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            dev.bufferSizeSet(size)

            low_level_patch.FDwfDigitalInBufferSizeSet.assert_called_once_with(dev.hdwf, size)

def test_buffer_size_get():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            value = dev.bufferSizeGet()

            low_level_patch.FDwfDigitalInBufferSizeGet.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalInBufferSizeGet.return_value

@pytest.mark.parametrize('sample_mode', dwf.DwfDigitalIn.SAMPLEMODE)
def test_sample_mode_info(sample_mode):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            low_level_patch.FDwfDigitalInSampleModeInfo.return_value == sample_mode

            value = dev.sampleModeInfo()

            low_level_patch.FDwfDigitalInSampleModeInfo.assert_called_once_with(dev.hdwf)

@pytest.mark.parametrize('sample_mode', dwf.DwfDigitalIn.SAMPLEMODE)
def test_sample_mode_set(sample_mode):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            dev.sampleModeSet(sample_mode)

            low_level_patch.FDwfDigitalInSampleModeSet.assert_called_once_with(dev.hdwf, sample_mode)

@pytest.mark.parametrize('sample_mode', dwf.DwfDigitalIn.SAMPLEMODE)
def test_sample_mode_get(sample_mode):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            low_level_patch.FDwfDigitalInSampleModeGet.return_value = sample_mode

            value = dev.sampleModeGet()

            low_level_patch.FDwfDigitalInSampleModeGet.assert_called_once_with(dev.hdwf)
            assert value == sample_mode

@pytest.mark.parametrize('acq_mode', dwf.DwfDigitalIn.ACQMODE)
def test_acq_mode_info(acq_mode):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            low_level_patch.FDwfDigitalInAcquisitionModeInfo.return_value == acq_mode

            value = dev.acquisitionModeInfo()

            low_level_patch.FDwfDigitalInAcquisitionModeInfo.assert_called_once_with(dev.hdwf)

@pytest.mark.parametrize('acq_mode', dwf.DwfDigitalIn.ACQMODE)
def test_acq_mode_set(acq_mode):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            dev.acquisitionModeSet(acq_mode)

            low_level_patch.FDwfDigitalInAcquisitionModeSet.assert_called_once_with(dev.hdwf, acq_mode)

@pytest.mark.parametrize('acq_mode', dwf.DwfDigitalIn.ACQMODE)
def test_acq_mode_get(acq_mode):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            low_level_patch.FDwfDigitalInAcquisitionModeGet.return_value = acq_mode

            value = dev.acquisitionModeGet()

            low_level_patch.FDwfDigitalInAcquisitionModeGet.assert_called_once_with(dev.hdwf)
            assert value == acq_mode

@pytest.mark.parametrize('trig_src', dwf.DwfDigitalIn.TRIGSRC)
def test_trig_src_info(trig_src):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            low_level_patch.FDwfDigitalInTriggerSourceInfo.return_value == trig_src

            value = dev.triggerSourceInfo()

            low_level_patch.FDwfDigitalInTriggerSourceInfo.assert_called_once_with(dev.hdwf)

@pytest.mark.parametrize('trig_src', dwf.DwfDigitalIn.TRIGSRC)
def test_trig_src_set(trig_src):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            dev.triggerSourceSet(trig_src)

            low_level_patch.FDwfDigitalInTriggerSourceSet.assert_called_once_with(dev.hdwf, trig_src)

@pytest.mark.parametrize('trig_src', dwf.DwfDigitalIn.TRIGSRC)
def test_trig_src_get(trig_src):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            low_level_patch.FDwfDigitalInTriggerSourceGet.return_value = trig_src

            value = dev.triggerSourceGet()

            low_level_patch.FDwfDigitalInTriggerSourceGet.assert_called_once_with(dev.hdwf)
            assert value == trig_src

def test_trigger_position_info():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            value = dev.triggerPositionInfo()

            low_level_patch.FDwfDigitalInTriggerPositionInfo.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalInTriggerPositionInfo.return_value

@pytest.mark.parametrize('samples', [1, 100])
def test_trigger_position_set(samples):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            dev.triggerPositionSet(samples)

            low_level_patch.FDwfDigitalInTriggerPositionSet.assert_called_once_with(dev.hdwf, samples)

def test_trigger_position_get():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            value = dev.triggerPositionGet()

            low_level_patch.FDwfDigitalInTriggerPositionGet.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalInTriggerPositionGet.return_value

def test_trigger_auto_timeout_info():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            value = dev.triggerAutoTimeoutInfo()

            low_level_patch.FDwfDigitalInTriggerAutoTimeoutInfo.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalInTriggerAutoTimeoutInfo.return_value

@pytest.mark.parametrize('value', [0, 100])
def test_trigger_auto_timeout_set(value):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            dev.triggerAutoTimeoutSet(value)

            low_level_patch.FDwfDigitalInTriggerAutoTimeoutSet.assert_called_once_with(dev.hdwf, value)

def test_trigger_auto_timeout_get():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            value = dev.triggerAutoTimeoutGet()

            low_level_patch.FDwfDigitalInTriggerAutoTimeoutGet.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalInTriggerAutoTimeoutGet.return_value

def test_trigger_info():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()
            value = dev.triggerInfo()

            low_level_patch.FDwfDigitalInTriggerInfo.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalInTriggerInfo.return_value

@pytest.mark.parametrize('triggers', [(1, 2, 3, 4)])
def test_trigger_set(triggers):
    (low_level, high_level, rising_edge, falling_edge) = triggers

    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()

            dev.triggerSet(low_level, high_level, rising_edge, falling_edge)

            low_level_patch.FDwfDigitalInTriggerSet.assert_called_once_with(dev.hdwf, low_level, high_level, rising_edge, falling_edge)

def test_trigger_get():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalIn()
            value = dev.triggerGet()

            low_level_patch.FDwfDigitalInTriggerGet.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalInTriggerGet.return_value
