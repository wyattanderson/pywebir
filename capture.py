import sys, time, logging, tempfile, json, base64
from twisted.python import usage, log
from twisted.internet import protocol

class IrToy(protocol.Protocol):
    def __init__(self, options):
        self.sleep_time = 0.005
        self.handshake  = None
        self.byte_count = 0
        self.complete   = None
        self.state = 'set_mode'
        self.rbuf = bytearray()
        self.wbuf = bytearray()
        self.wbuf_cursor = 0
        self.output_dir = options['dir']
        self.options = options
        self.send_remaining = 0

    def _sleep(self):
        time.sleep(self.sleep_time)

    def connectionMade(self):
        """ Reset the device to make sure we get it out of any mode it's in
        and then set it to sampling mode """
        self._sleep()
        self.transport.writeSomeData("\0\0\0\0\0")
        self._sleep()
        self.transport.writeSomeData("S")
        self._sleep()

    def ready(self):
        pass

    def _state_set_mode(self, byte):
        if len(self.rbuf) == 3:
            self.rbuf = bytearray()
            self.ready()
            return 'recv'
        else:
            return 'set_mode'

    def _state_recv(self, byte):
        if self.rbuf.endswith(b'\xff\xff'):
            with tempfile.NamedTemporaryFile(prefix='ir-',
                    dir=self.output_dir,
                    suffix='.bin',
                    delete=False) as f:
                f.write(self.rbuf)
                log.msg("Wrote IR file %s" % f.name)

            self.rbuf = bytearray()
            return 'recv'
        return 'recv'

    def _state_exit(self, *args):
        self._sleep()
        self.transport.writeSomeData("\0")
        self._sleep()
        reactor.stop()
        raise SystemExit

    def dataReceived(self, data):
        log.msg("Data: %s" % ["%#x" % ord(byte) for byte in data])

        for c in data:
            byte = ord(c)
            self.rbuf.append(byte)
            self.state = getattr(self, '_state_'+self.state)(byte)

class TransmitIrToy(IrToy):
    def _state_recv(self, byte):
        if byte == 0x3E and self.wbuf_cursor < len(self.wbuf):
            self.send_remaining = 0x3E
            return self._state_start_xmit(byte)
        elif byte == ord('C'):
            return self._state_exit(byte)
        else:
            return 'recv'

    def _state_start_xmit(self, byte):
        self._sleep()
        buf_slice = self.wbuf[
                self.wbuf_cursor:self.wbuf_cursor+self.send_remaining]
        self.transport.write("".join(map(chr, buf_slice)))
        self.wbuf_cursor += len(buf_slice)
        return 'recv'

    def ready(self):
        self.setTransmitMode()

    def setTransmitMode(self):
        self._sleep()

        with open(self.options['file'], 'r') as infile:
            button_data = json.load(infile)
            self.wbuf = bytearray(
                    base64.b64decode(button_data['irdata']))

        # Enable transmit handshake, return transmit count and notify on
        # complete
        self.transport.writeSomeData("\x26\x25\x24")

        # Enter transmit mode
        self._sleep()
        self.transport.writeSomeData("\x03")

class Options(usage.Options):
    optParameters = [
            ['port', 'p', '/dev/ttyACM0', 'ir toy'],
            ['dir', 'd', None, 'directory'],
            ['mode', 'm', 'recv', 'mode'],
            ['file', 'f', None, 'xmit file'],
        ]

if __name__ == '__main__':
    from twisted.internet import reactor
    from twisted.internet.serialport import SerialPort
    o = Options()
    try:
        o.parseOptions()
    except usage.UsageError, errortext:
        raise SystemExit

    logFile = sys.stdout
    log.startLogging(logFile)

    if o.opts['mode'] == 'xmit':
        SerialPort(TransmitIrToy(o.opts), o.opts['port'], reactor, baudrate=115200)
    else:
        SerialPort(IrToy(o.opts), o.opts['port'], reactor, baudrate=115200)
    reactor.run()
