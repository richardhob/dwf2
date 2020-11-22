Forum post about configuring the device with "parameters":

    https://forum.digilentinc.com/topic/19063-intelligent-record-mode-for-the-logic-analyzer/

It looks to me (after much searching) that these are used IN ADDITTION to the
`idxCfg` parameter. The `idxCfg` MUST be dependant on what device is selected,
so it may be hard to generalize.

# All Examples

All examples provided by Digilent are included in the Waveforms installation. On
Linux, this (sometimes) can be found at:

    usr/share/digilent/waveforms/samples

These include (but aren't limited to):

- UART
- SPI
- I2C
- CAN
- Large Acquisitions
- Others!


