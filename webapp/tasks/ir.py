import serial
import time

from webapp.tasks import celery
from capture import TransmitIrToy
from celery.signals import worker_shutdown

def sleep():
    time.sleep(0.05)

@celery.task
def send_ir_command(irdata):
    sp = serial.Serial('/dev/ttyACM0')
    sp.write("\0\0\0\0\0")
    sleep()
    sp.write("S")
    sleep()
    sp.write("\x03")
    sleep()
    sp.write(irdata)
    sleep()
    sp.write("\0")
    sleep()
    sp.close()
    return
