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

def test_repeat_info():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            value = dev.repeatInfo()

            low_level_patch.FDwfDigitalOutRepeatInfo.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalOutRepeatInfo.return_value

@pytest.mark.parametrize('count', [0, 100])
def test_repeat_set(count):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            dev.repeatSet(count)

            low_level_patch.FDwfDigitalOutRepeatSet.assert_called_once_with(dev.hdwf, count)

def test_repeat_get():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            value = dev.repeatGet()
            low_level_patch.FDwfDigitalOutRepeatGet.assert_called_once_with(dev.hdwf)

            assert value == low_level_patch.FDwfDigitalOutRepeatGet.return_value

def test_repeat_status():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            value = dev.repeatStatus()
            low_level_patch.FDwfDigitalOutRepeatStatus.assert_called_once_with(dev.hdwf)

            assert value == low_level_patch.FDwfDigitalOutRepeatStatus.return_value

@pytest.mark.parametrize('repeat', [False, True])
def test_repeat_trigger_set(repeat):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            dev.repeatTriggerSet(repeat)

            low_level_patch.FDwfDigitalOutRepeatTriggerSet.assert_called_once_with(dev.hdwf, repeat)

@pytest.mark.parametrize('repeat', [False, True])
def test_repeat_trigger_get(repeat):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            low_level_patch.FDwfDigitalOutRepeatTriggerGet.return_value = repeat

            value = dev.repeatTriggerGet()

            low_level_patch.FDwfDigitalOutRepeatTriggerGet.assert_called_once_with(dev.hdwf)
            assert value == repeat

def test_channel_count():
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            value = dev.channelCount()

            low_level_patch.FDwfDigitalOutCount.assert_called_once_with(dev.hdwf)
            assert value == low_level_patch.FDwfDigitalOutCount.return_value

@pytest.mark.parametrize('channel', [0, 21])
@pytest.mark.parametrize('state', [False, True])
def test_enable_set(channel, state):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            dev.enableSet(channel, state)

            low_level_patch.FDwfDigitalOutEnableSet.assert_called_with(dev.hdwf, channel, state)

@pytest.mark.parametrize('channel', [0, 21])
@pytest.mark.parametrize('state', [False, True])
def test_enable_get(channel, state):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            low_level_patch.FDwfDigitalOutEnableGet.return_value = state

            value = dev.enableGet(channel)
            low_level_patch.FDwfDigitalOutEnableGet.assert_called_once_with(dev.hdwf, channel)

            assert value == state

@pytest.mark.parametrize('channel', [0, 21])
def test_output_info(channel):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            dev.outputInfo(channel)

            low_level_patch.FDwfDigitalOutOutputInfo.assert_called_once_with(dev.hdwf, channel)

@pytest.mark.parametrize('channel', [0, 21])
@pytest.mark.parametrize('output_type', dwf.DwfDigitalOut.OUTPUT)
def test_output_set(channel, output_type):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            dev.outputSet(channel, output_type)

            low_level_patch.FDwfDigitalOutOutputSet.assert_called_once_with(dev.hdwf, channel, output_type)

@pytest.mark.parametrize('channel', [0, 21])
@pytest.mark.parametrize('output_type', dwf.DwfDigitalOut.OUTPUT)
def test_output_get(channel, output_type):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            low_level_patch.FDwfDigitalOutOutputGet.return_value = output_type

            value = dev.outputGet(channel)

            low_level_patch.FDwfDigitalOutOutputGet.assert_called_once_with(dev.hdwf, channel)
            assert value == output_type

@pytest.mark.parametrize('channel', [0, 21])
def test_type_info(channel):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            dev.typeInfo(channel)

            low_level_patch.FDwfDigitalOutTypeInfo.assert_called_once_with(dev.hdwf, channel)

@pytest.mark.parametrize('channel', [0, 21])
@pytest.mark.parametrize('channel_type', dwf.DwfDigitalOut.TYPE)
def test_type_set(channel, channel_type):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            dev.typeSet(channel, channel_type)

            low_level_patch.FDwfDigitalOutTypeSet.assert_called_once_with(dev.hdwf, channel, channel_type)

@pytest.mark.parametrize('channel', [0, 21])
@pytest.mark.parametrize('channel_type', dwf.DwfDigitalOut.TYPE)
def test_type_get(channel, channel_type):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            low_level_patch.FDwfDigitalOutTypeGet.return_value = channel_type

            value = dev.typeGet(channel)

            low_level_patch.FDwfDigitalOutTypeGet.assert_called_once_with(dev.hdwf, channel)
            assert value == channel_type

@pytest.mark.parametrize('channel', [0, 21])
def test_idle_info(channel):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            dev.idleInfo(channel)

            low_level_patch.FDwfDigitalOutIdleInfo.assert_called_once_with(dev.hdwf, channel)

@pytest.mark.parametrize('channel', [0, 21])
@pytest.mark.parametrize('idle_state', dwf.DwfDigitalOut.IDLE)
def test_idle_set(channel, idle_state):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            dev.idleSet(channel, idle_state)

            low_level_patch.FDwfDigitalOutIdleSet.assert_called_once_with(dev.hdwf, channel, idle_state)

@pytest.mark.parametrize('channel', [0, 21])
@pytest.mark.parametrize('idle_state', dwf.DwfDigitalOut.IDLE)
def test_idle_get(channel, idle_state):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            low_level_patch.FDwfDigitalOutIdleGet.return_value = idle_state

            value = dev.idleGet(channel)

            low_level_patch.FDwfDigitalOutIdleGet.assert_called_once_with(dev.hdwf, channel)
            assert value == idle_state

@pytest.mark.parametrize('channel', [0, 21])
def test_divider_info(channel):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            dev.dividerInfo(channel)

            low_level_patch.FDwfDigitalOutDividerInfo.assert_called_once_with(dev.hdwf, channel)

@pytest.mark.parametrize('channel', [0, 21])
@pytest.mark.parametrize('divider', [12, 1])
def test_divider_init_set(channel, divider):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            dev.dividerInitSet(channel, divider)

            low_level_patch.FDwfDigitalOutDividerInitSet.assert_called_once_with(dev.hdwf, channel, divider)

@pytest.mark.parametrize('channel', [0, 21])
@pytest.mark.parametrize('divider', [12, 1])
def test_divider_init_get(channel, divider):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            low_level_patch.FDwfDigitalOutDividerInitGet.return_value = divider

            value = dev.dividerInitGet(channel)

            low_level_patch.FDwfDigitalOutDividerInitGet.assert_called_once_with(dev.hdwf, channel)
            assert value == divider

@pytest.mark.parametrize('channel', [0, 21])
@pytest.mark.parametrize('divider', [12, 1])
def test_divider_set(channel, divider):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            dev.dividerSet(channel, divider)

            low_level_patch.FDwfDigitalOutDividerSet.assert_called_once_with(dev.hdwf, channel, divider)

@pytest.mark.parametrize('channel', [0, 21])
@pytest.mark.parametrize('divider', [12, 1])
def test_divider_get(channel, divider):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            low_level_patch.FDwfDigitalOutDividerGet.return_value = divider

            value = dev.dividerGet(channel)

            low_level_patch.FDwfDigitalOutDividerGet.assert_called_once_with(dev.hdwf, channel)
            assert value == divider

@pytest.mark.parametrize('channel', [0, 21])
def test_counter_info(channel):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            dev.counterInfo(channel)

            low_level_patch.FDwfDigitalOutCounterInfo.assert_called_once_with(dev.hdwf, channel)

@pytest.mark.parametrize('channel', [0, 21])
@pytest.mark.parametrize('state', [False, True])
@pytest.mark.parametrize('value', [0, 0xFF])
def test_counter_init_set(channel, value, state):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            dev.counterInitSet(channel, state, value)

            low_level_patch.FDwfDigitalOutCounterInitSet.assert_called_once_with(dev.hdwf, channel, state, value)

@pytest.mark.parametrize('channel', [0, 21])
@pytest.mark.parametrize('counter', [12, 1])
def test_counter_init_get(channel, counter):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            low_level_patch.FDwfDigitalOutCounterInitGet.return_value = counter

            value = dev.counterInitGet(channel)

            low_level_patch.FDwfDigitalOutCounterInitGet.assert_called_once_with(dev.hdwf, channel)
            assert value == counter

@pytest.mark.parametrize('channel', [0, 21])
@pytest.mark.parametrize('low', [12, 2])
@pytest.mark.parametrize('high', [0, 1])
def test_counter_set(channel, low, high):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            dev.counterSet(channel, low, high)

            low_level_patch.FDwfDigitalOutCounterSet.assert_called_once_with(dev.hdwf, channel, low, high)

@pytest.mark.parametrize('channel', [0, 21])
@pytest.mark.parametrize('counter', [12, 1])
def test_counter_get(channel, counter):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            low_level_patch.FDwfDigitalOutCounterGet.return_value = counter

            value = dev.counterGet(channel)

            low_level_patch.FDwfDigitalOutCounterGet.assert_called_once_with(dev.hdwf, channel)
            assert value == counter

@pytest.mark.parametrize('channel', [0, 21])
def test_data_info(channel):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            value = dev.dataInfo(channel)

            low_level_patch.FDwfDigitalOutDataInfo.assert_called_once_with(dev.hdwf, channel)
            assert value == low_level_patch.FDwfDigitalOutDataInfo.return_value

@pytest.mark.parametrize('channel', [0, 21])
@pytest.mark.parametrize('bits', [0, 1, 2, 3])
def test_data_set(channel, bits):
    with unittest.mock.patch.object(dwf.api, "_HDwf") as hdwf_patch:
        with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
            dev = dwf.DwfDigitalOut()

            dev.dataSet(channel, bits)

            low_level_patch.FDwfDigitalOutDataSet.assert_called_once_with(dev.hdwf, channel, bits)
