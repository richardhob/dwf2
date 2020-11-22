
import unittest.mock

import pytest

import dwf

def test_dwf_init_default():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.Dwf()

            low_level_patch.FDwfDeviceOpen.assert_called_once_with(-1)
            hdwf_patch.assert_called_once_with(low_level_patch.FDwfDeviceOpen.return_value)

@pytest.mark.parametrize('device_id', [-1, 0, 100])
def test_dwf_init_device_id(device_id):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.Dwf(device_id)

            low_level_patch.FDwfDeviceOpen.assert_called_once_with(device_id)
            hdwf_patch.assert_called_once_with(low_level_patch.FDwfDeviceOpen.return_value)

@pytest.mark.parametrize('device_id', [-1, 0, 100])
@pytest.mark.parametrize('device_cfg', [0, 100])
def test_dwf_init_device_id_and_device_config(device_id, device_cfg):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.Dwf(device_id, device_cfg)

            low_level_patch.FDwfDeviceConfigOpen.assert_called_once_with(device_id, device_cfg)
            hdwf_patch.assert_called_once_with(low_level_patch.FDwfDeviceConfigOpen.return_value)

def test_dwf_init_none():
    with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
        low_level_patch.FDwfDeviceOpen.return_value = dwf.Dwf.DEVICE_NONE

        with pytest.raises(RuntimeError):
            dwf.Dwf()

def test_dwf_close():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.Dwf()
            dev.close()

            dev.hdwf.close.assert_called_once()

@pytest.mark.parametrize('config', [True, False])
def test_dwf_auto_configure_set(config):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.Dwf()

            dev.autoConfigureSet(config)

            low_level_patch.FDwfDeviceAutoConfigureSet.assert_called_once_with( dev.hdwf, config)

def test_dwf_auto_configure_get():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.Dwf()

            dev.autoConfigureGet()

            low_level_patch.FDwfDeviceAutoConfigureGet.assert_called_once()

def test_dwf_reset():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.Dwf()

            dev.reset()

            low_level_patch.FDwfDeviceReset.assert_called_once()

@pytest.mark.parametrize('config', [True, False])
def test_dwf_enable_set(config):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.Dwf()

            dev.enableSet(config)

            low_level_patch.FDwfDeviceEnableSet.assert_called_once_with(dev.hdwf, config)
