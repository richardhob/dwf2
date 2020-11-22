
import unittest.mock

import pytest

import dwf
from dwf.api import _HDwf

def test_hdwf_init():
    dev = _HDwf('test')
    dev.__del__ = unittest.mock.MagicMock()

    assert dev.hdwf == 'test'
    assert dev._as_parameter_ =='test'

def test_hdwf_close_ok():
    with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
        dev = _HDwf('test')
        dev.__del__ = unittest.mock.MagicMock()

        dev.close()
        low_level_patch.FDwfDeviceClose.assert_called_once_with('test')

def test_hdwf_close_not_ok():
    with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
        dev = _HDwf(low_level_patch.hdwfNone)
        dev.__del__ = unittest.mock.MagicMock()

        dev.close()
        assert low_level_patch.called == 0
