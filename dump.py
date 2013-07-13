import pprint
import serial
import sys
import time

def sleep():
    time.sleep(0.05)

with open(sys.argv[1], 'r') as infile:
    buf = bytearray(infile.read())
    sp = serial.Serial('/dev/ttyACM0')
    sp.write(b"\0")
    sleep()
    sp.write(b"S")
    sleep()
    sp.write(b"\x03")
    sleep()
    sp.write(buf)
    sleep()
    sp.write(b"\0")
    sleep()
    sp.write(b"S")
    sleep()
    sp.close()

def writelist(buf, sp):
    sleep()

    bytesWritten = 0
    maxWriteSize = 32
    for i in range(0, len(buf), maxWriteSize):
        segmentWritten = sp.write(buf[i:i+maxWriteSize])
        bytesWritten += segmentWritten
