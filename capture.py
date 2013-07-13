import sys, time, logging, tempfile
from twisted.python import usage, log
from twisted.internet import protocol

class IrToy(protocol.Protocol):
    def __init__(self, options):
        self.sleep_time = 0.05
        self.handshake  = None
        self.byte_count = 0
        self.complete   = None
        self.state = 'set_mode'
        self.buffer = bytearray()
        self.output_dir = options['dir']

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

    def state_set_mode(self, byte):
        if len(self.buffer) == 3:
            self.buffer = bytearray()
            return 'recv'
        else:
            return 'set_mode'

    def state_recv(self, byte):
        if self.buffer.endswith(b'\xff\xff'):
            with tempfile.NamedTemporaryFile(prefix='ir-',
                    dir=self.output_dir,
                    suffix='.bin',
                    delete=False) as f:
                f.write(self.buffer)
                log.msg("Wrote IR file %s" % f.name)

            self.buffer = bytearray()
            return 'recv'
        return 'recv'

    def dataReceived(self, data):
        log.msg("Data: %s" % ["%#x" % ord(byte) for byte in data])

        for c in data:
            byte = ord(c)
            self.buffer.append(byte)
            self.state = getattr(self, 'state_'+self.state)(byte)

class Options(usage.Options):
    optParameters = [
            ['port', 'p', '/dev/ttyACM0', 'ir toy'],
            ['dir', 'd', None, 'directory']
        ]

if __name__ == '__main__':
    from twisted.internet import reactor
    from twisted.internet.serialport import SerialPort
    o = Options()
    try:
        o.parseOptions()
    except usage.UsageError, errortext:
        print "nope"
        raise SystemExit

    logFile = sys.stdout
    log.startLogging(logFile)

    SerialPort(IrToy(o.opts), o.opts['port'], reactor, baudrate=115200)
    reactor.run()
