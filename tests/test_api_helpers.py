#! /usr/bin/env python
# -*- coding: utf-8 -*-

import enum
import unittest.mock

import pytest

import dwf
from dwf.api import _make_set

class DummyEnum(enum.IntEnum):
    A = 0
    B = 1
    C = 2
    D = 3

# Expected values for `test_make_set`
EXPECTED = [
    (0xF, frozenset((DummyEnum.A, DummyEnum.B, DummyEnum.C, DummyEnum.D))),
    (0x9, frozenset((DummyEnum.A, DummyEnum.D))),
    (0x0, frozenset(())),
]

@pytest.mark.parametrize("value,expected", EXPECTED)
def test_make_set(value, expected):
    # Helper function used a lot in dwf.api
    actual = _make_set(value, expected)
    assert actual == expected

@pytest.mark.parametrize('param', dwf.ENUMFILTER)
def test_dwf_enumeration(param):
    with unittest.mock.patch.object(dwf.api, '_l') as low_level_patch:
        with unittest.mock.patch.object(dwf.api, 'DwfDevice') as dev_patch:
            low_level_patch.FDwfEnum.return_value = 1
            value = dwf.DwfEnumeration(param)

            # Was FDwfEnum called with `param`
            low_level_patch.FDwfEnum.assert_called_once_with(param)

            # Was DwfDevice instantiated with the correct index
            dev_patch.assert_called_once_with(0)
