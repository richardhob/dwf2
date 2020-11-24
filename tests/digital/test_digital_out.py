#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest.mock

import pytest

import dwf

def test_init_default():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            low_level_patch.FDwfDeviceOpen.assert_called_once_with(-1)
            hdwf_patch.assert_called_once_with(low_level_patch.FDwfDeviceOpen.return_value)

@pytest.mark.parametrize('device_id', [-1, 0, 100])
def test_init_device_id(device_id):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut(device_id)

            low_level_patch.FDwfDeviceOpen.assert_called_once_with(device_id)
            hdwf_patch.assert_called_once_with(low_level_patch.FDwfDeviceOpen.return_value)

@pytest.mark.parametrize('device_id', [-1, 0, 100])
@pytest.mark.parametrize('device_cfg', [0, 100])
def test_init_device_id_and_device_config(device_id, device_cfg):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut(device_id, device_cfg)

            low_level_patch.FDwfDeviceConfigOpen.assert_called_once_with(device_id, device_cfg)
            hdwf_patch.assert_called_once_with(low_level_patch.FDwfDeviceConfigOpen.return_value)

def test_init_none():
    with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
        low_level_patch.FDwfDeviceOpen.return_value = dwf.Dwf.DEVICE_NONE

        with pytest.raises(RuntimeError):
            dwf.DwfDigitalOut()

def test_init_dwf():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.Dwf()
            digital_dev = dwf.DwfDigitalOut(dev)

            low_level_patch.FDwfDeviceOpen.assert_called_once_with(-1)
            hdwf_patch.assert_called_once_with(low_level_patch.FDwfDeviceOpen.return_value)

def test_digital_out_reset():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()
            dev.reset()

            low_level_patch.FDwfDigitalOutReset.assert_called_once_with(dev.hdwf)

def test_device_in_reset():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()
            dev.reset(parent=True)

            low_level_patch.FDwfDeviceReset.assert_called_once_with(dev.hdwf)

@pytest.mark.parametrize('start_stop', [True, False])
def test_configure(start_stop):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            dev.configure(start_stop)

            low_level_patch.FDwfDigitalOutConfigure.assert_called_once_with(dev.hdwf, start_stop)

@pytest.mark.parametrize('state', dwf.Dwf.STATE)
def status(state):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()
            low_level_patch.FDwfDigitalOutStatus.return_value = state

            value = dev.status(state)

            low_level_patch.FDwfDigitalOutStatus.assert_called_once_with(dev.hdwf, state)
            assert value == state

def test_internal_clock_info():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            value = dev.internalClockInfo()

            low_level_patch.FDwfDigitalOutInternalClockInfo.assert_called_once_with(dev.hdwf)

            assert value == low_level_patch.FDwfDigitalOutInternalClockInfo.return_value

def test_trigger_source_info():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            dev.triggerSourceInfo()

            low_level_patch.FDwfDigitalOutTriggerSourceInfo.assert_called_once_with(dev.hdwf)

@pytest.mark.parametrize('trigger', dwf.Dwf.TRIGSRC)
def test_trigger_source_set(trigger):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            dev.triggerSourceSet(trigger)

            low_level_patch.FDwfDigitalOutTriggerSourceSet.assert_called_once_with(dev.hdwf, trigger)

@pytest.mark.parametrize('trigger', dwf.Dwf.TRIGSRC)
def test_trigger_source_get(trigger):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            low_level_patch.FDwfDigitalOutTriggerSourceGet.return_value = trigger
            value = dev.triggerSourceGet()

            low_level_patch.FDwfDigitalOutTriggerSourceGet.assert_called_once_with(dev.hdwf)
            assert value == trigger

def test_run_info():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            value = dev.runInfo()

            low_level_patch.FDwfDigitalOutRunInfo.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalOutRunInfo.return_value

@pytest.mark.parametrize('run_time', [0, 10.0])
def test_run_set(run_time):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            dev.runSet(run_time)

            low_level_patch.FDwfDigitalOutRunSet.assert_called_once_with(dev.hdwf, run_time)

def test_run_get():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            value = dev.runGet()

            low_level_patch.FDwfDigitalOutRunGet.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalOutRunGet.return_value

def test_run_status():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            value = dev.runStatus()

            low_level_patch.FDwfDigitalOutRunStatus.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalOutRunStatus.return_value

def test_wait_info():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            value = dev.waitInfo()

            low_level_patch.FDwfDigitalOutWaitInfo.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalOutWaitInfo.return_value

@pytest.mark.parametrize('wait_time', [0, 1.0])
def test_wait_set(wait_time):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            dev.waitSet(wait_time)

            low_level_patch.FDwfDigitalOutWaitSet.assert_called_once_with(dev.hdwf, wait_time)

def test_wait_get():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            value = dev.waitGet()

            low_level_patch.FDwfDigitalOutWaitGet.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalOutWaitGet.return_value


