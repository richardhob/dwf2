
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
