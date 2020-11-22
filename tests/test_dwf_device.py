
import unittest.mock

import pytest

import dwf

@pytest.fixture
def dev():
    device = dwf.DwfDevice(0)
    return device

@pytest.mark.parametrize('index', [0, -1, 10])
def test_dwf_device_init(index):
    dev = dwf.DwfDevice(index)
    assert dev.idxDevice == index

@pytest.mark.parametrize('device_id', dwf.DwfDevice.DEVID)
@pytest.mark.parametrize('device_version', dwf.DwfDevice.DEVVER)
def test_device_type(dev, device_id, device_version):
    with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
        low_level_patch.FDwfEnumDeviceType.return_value = (device_id, device_version)

        actual_id, actual_version = dev.deviceType()

        low_level_patch.FDwfEnumDeviceType.assert_called_once_with(dev.idxDevice)

        assert actual_id == device_id
        assert device_version == actual_version

@pytest.mark.parametrize('output', [0, 1])
def test_device_is_opened(dev, output):
    with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
        low_level_patch.FDwfEnumDeviceIsOpened.return_value = output

        value = dev.isOpened()

        low_level_patch.FDwfEnumDeviceIsOpened.assert_called_once_with(dev.idxDevice)

        assert value == bool(output)

def test_device_user_name(dev):
    with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
        low_level_patch.FDwfEnumUserName.return_value = 'test'

        name = dev.userName()

        low_level_patch.FDwfEnumUserName.assert_called_once_with(dev.idxDevice)

        assert name == 'test'

def test_device_name(dev):
    with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
        low_level_patch.FDwfEnumDeviceName.return_value = 'test'

        name = dev.deviceName()

        low_level_patch.FDwfEnumDeviceName.assert_called_once_with(dev.idxDevice)

        assert name == 'test'

def test_device_serial_number(dev):
    with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
        low_level_patch.FDwfEnumSN.return_value = 'test'

        name = dev.SN()

        low_level_patch.FDwfEnumSN.assert_called_once_with(dev.idxDevice)

        assert name == 'test'

def test_device_config(dev):
    with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
        low_level_patch.FDwfEnumConfig.return_value = 'test'

        name = dev.config()

        low_level_patch.FDwfEnumConfig.assert_called_once_with(dev.idxDevice)

        assert name == 'test'

@pytest.mark.parametrize('info', dwf.DwfDevice.CONFIGINFO)
def test_device_config_info(dev, info):
    with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
        low_level_patch.FDwfEnumConfigInfo.return_value = 'test'

        name = dev.configInfo(info)

        low_level_patch.FDwfEnumConfigInfo.assert_called_once_with(dev.idxDevice,
                info)

        assert name == 'test'

def test_device_open(dev):
    with unittest.mock.patch.object(dwf.api, 'Dwf') as dwf_patch:
        dev.open(config='test')
        dwf_patch.assert_called_once_with(dev.idxDevice, idxCfg='test')
