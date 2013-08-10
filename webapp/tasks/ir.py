import serial
import time

from capture import TransmitIrToy
from celery.signals import worker_shutdown
from celery.utils.log import get_task_logger
from webapp import settings
from webapp.tasks import celery

logger = get_task_logger(__name__)

def sleep():
    time.sleep(0.25)

@celery.task
def send_ir_command(irdata):
    if settings.SKIP_IR:
        logger.warn("Received IR command, but skipping transmission")
        return

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
