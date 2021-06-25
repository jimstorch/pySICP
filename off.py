#!/usr/bin/env python3

import serial

"""
Control Philips Digital Signage via the serial port.
Requires pyserial:
    pip3 install pyserial
This is an older device that uses SICP v1.7 (no Group byte)
Note that you may need to add yourself to the 'dialout' group in Linux.
"""

DEVICE = '/dev/ttyUSB0'
MONITOR = 0x01
SET_POWER_STATE = 0x18
PWR_OFF = 0x01
PWR_ON = 0x02

with serial.Serial() as ser:
    ser.baudrate = 9600
    ser.port = DEVICE
    ser.open()
    ser.timeout = .25
    #print(ser)

    def checksum(data):
        # Calculate checksum by Exclusive Or'ing each byte
        c = data[0]
        for b in data[1:]:
            c ^= b
        return c

    def checksum_write(data):
        packet = bytearray()
        # First byte is the packet length
        # to which we add one byte for leading length byte itself
        # and another for the trailing checksum byte

        # TIL: Use bytearray.append() for Integer Objects
        #      and bytearray.extend() for Byte Objects.
        packet.append(len(data) + 2)
        packet.extend(data)
        packet.append(checksum(packet))
        print('Sending packet ', packet)
        ser.write(packet)

    cmd = [MONITOR, SET_POWER_STATE, PWR_OFF]
    checksum_write(cmd)
    resp = ser.read(40)
    #print(resp)
    if resp == b'\x05\x01\x00\x06\x02':
        print('CMD OK')
    else:
        print('Bad response ', resp)
