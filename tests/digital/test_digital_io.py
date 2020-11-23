#! /usr/bin/env python

''' Test the DWF Digtital IO class, DwfDigitalIO '''

import unittest.mock

import pytest

import dwf

@pytest.fixture(scope='module')
def dio(request):
    ''' Mock up the Digital IO class by `patching` the low level API
    (dwf.api._l), and verifying the correct functions are called.
    '''
    patcher = unittest.mock.patch.object(dwf.api, '_l')

    low_level_patch = patcher.start()
    dwf_dio = dwf.DwfDigitalIO()

    # Make sure that the HDWF Close doesn't get called (throws an error due to
    # back mocking
    dwf_dio.hdwf.close = unittest.mock.MagicMock()

    def _close():
        patcher.stop()

    request.addfinalizer(_close)
    return (dwf_dio, low_level_patch)

def test_digital_reset(dio):
    dwf_dio, low_level_patch = dio

    dwf_dio.reset()
    low_level_patch.FDwfDigitalIOReset.assert_called_once_with(dwf_dio.hdwf)

def test_device_reset(dio):
    dwf_dio, low_level_patch = dio

    dwf_dio.reset(parent=True)
    low_level_patch.FDwfDeviceReset.assert_called_once_with(dwf_dio.hdwf)

def test_configure(dio):
    dwf_dio, low_level_patch = dio

    dwf_dio.configure()
    low_level_patch.FDwfDigitalIOConfigure.assert_called_once_with(dwf_dio.hdwf)

def test_status(dio):
    dwf_dio, low_level_patch = dio

    dwf_dio.status()
    low_level_patch.FDwfDigitalIOStatus.assert_called_once_with(dwf_dio.hdwf)

def test_output_enable_info(dio):
    dwf_dio, low_level_patch = dio

    value = dwf_dio.outputEnableInfo()

    assert value == low_level_patch.FDwfDigitalIOOutputEnableInfo.return_value
    low_level_patch.FDwfDigitalIOOutputEnableInfo.assert_called_once_with(dwf_dio.hdwf)

def test_output_enable_set(dio):
    dwf_dio, low_level_patch = dio

    dwf_dio.outputEnableSet(123)

    low_level_patch.FDwfDigitalIOOutputEnableSet.assert_called_once_with(dwf_dio.hdwf,
            123)

def test_output_enable_get(dio):
    dwf_dio, low_level_patch = dio

    value = dwf_dio.outputEnableGet()

    assert value == low_level_patch.FDwfDigitalIOOutputEnableGet.return_value
    low_level_patch.FDwfDigitalIOOutputEnableGet.assert_called_once_with(dwf_dio.hdwf)

def test_output_info(dio):
    dwf_dio, low_level_patch = dio

    value = dwf_dio.outputInfo()
    assert value == low_level_patch.FDwfDigitalIOOutputInfo.return_value
    low_level_patch.FDwfDigitalIOOutputInfo.assert_called_once_with(dwf_dio.hdwf)

def test_output_set(dio):
    dwf_dio, low_level_patch = dio

    dwf_dio.outputSet(0x123)

    low_level_patch.FDwfDigitalIOOutputSet.assert_called_once_with(dwf_dio.hdwf, 0x123)

def test_output_get(dio):
    dwf_dio, low_level_patch = dio

    value = dwf_dio.outputGet()

    assert value == low_level_patch.FDwfDigitalIOOutputGet.return_value
    low_level_patch.FDwfDigitalIOOutputGet.assert_called_once_with(dwf_dio.hdwf)

def test_input_info(dio):
    dwf_dio, low_level_patch = dio

    value = dwf_dio.inputInfo()

    assert value == low_level_patch.FDwfDigitalIOInputInfo.return_value
    low_level_patch.FDwfDigitalIOInputInfo.assert_called_once_with(dwf_dio.hdwf)

def test_input_status(dio):
    dwf_dio, low_level_patch = dio

    value = dwf_dio.inputStatus()

    assert value == low_level_patch.FDwfDigitalIOInputStatus.return_value
    low_level_patch.FDwfDigitalIOInputStatus.assert_called_once_with(dwf_dio.hdwf)
