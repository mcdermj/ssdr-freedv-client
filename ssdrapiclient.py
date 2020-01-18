import re

from twisted.internet.defer import inlineCallbacks, returnValue, Deferred
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineOnlyReceiver
from pexpect.fdpexpect import fdspawn
from sys import stdout
from typing import Tuple, List, Optional


class SsdrApiProtocol(LineOnlyReceiver):
    delimiter = b'\n'

    def __init__(self, vita_port: int) -> None:
        self.minor_version = 0.0
        self.major_version = 0.0
        self.handle = 0x00
        self.sequence = 0
        self.vita_port = vita_port
        self.meters = {}
        self.major_rev = 0
        self.minor_rev = 0
        self.handle = None
        self.expect = None
        self.freedv_slice = None
        self.slices = {}

    def send_command(self, command: str, wait: bool = True) -> Optional[Tuple[int, str]]:
        self.expect.sendline('C{}|{}'.format(self.sequence, command))
        matcher = 'R{}\|([0-9A-Z]{{0,8}})\|(.*)\n'.format(self.sequence)
        self.sequence = self.sequence + 1

        if wait:
            self.expect.expect(matcher)
            return int(self.expect.match.group(1)), self.expect.match.group(2)
        else:
            return None

    def load_meters(self) -> None:
        meter_attr_re = re.compile('(\d+)\.nam=([^#]+)')

        (code, message) = self.send_command('meter list')
        if code != 0:
            return None  # XXX Exception
        for match in meter_attr_re.finditer(message):
            print("Meter {} is #{}".format(match.group(2), match.group(1)))
            self.meters[match.group(2)] = match.group(1)

    def subscribe_meters(self, meters: List[str]) -> None:
        if len(self.meters) == 0:
            self.load_meters()

        for meter in meters:
            (code, message) = self.send_command('sub meter {}'.format(self.meters[meter]))
            if code != 0:
                print("Error subscribing meter {}({})".format(meter, self.meters[meter]))

    def connectionMade(self) -> None:
        self.expect = fdspawn(self.transport.getHandle().fileno(), timeout=10, encoding="utf-8", logfile=stdout)
        self.expect.expect('V(\d+\.\d+)\.(\d+\.\d+)\n')
        self.major_rev = self.expect.match.group(1)
        self.minor_rev = self.expect.match.group(2)
        print('Radio is Version {}/{}'.format(self.major_rev, self.minor_rev))

        self.expect.expect('H([0-9A-F]{8})\n')
        self.handle = self.expect.match.group(1)
        print('Our handle is {}'.format(self.handle))

        self.send_command('client udpport {}'.format(self.vita_port), wait=False)
        self.subscribe_meters([
            "fdv-snr",
            "fdv-foff",
            "fdv-total-bits",
            "fdv-error-bits",
            "fdv-ber"
        ])

        self.send_command('sub slice all', wait=False)

    def command_received(self, line):
        pass

    def status_received(self, line):
        line = line.split('|')[1]
        tokens = line.split()
        if tokens[0] == 'slice':
            sliceno = tokens[1]
            if sliceno not in self.slices:
                self.slices[sliceno] = {}
            for token in tokens[2:]:
                (name, value) = token.split('=')
                self.slices[sliceno][name] = value


    def message_received(selfs, line):
        pass

    def lineReceived(self, line):
        line = line.decode('utf-8')
        if line[0] == 'V':
            pass
        elif line[0] == 'H':
            pass
        elif line[0] == 'C':
            self.command_received(line)
        elif line[0] == 'R':
            pass
        elif line[0] == 'S':
            self.status_received(line)
        elif line[0] == 'M':
            self.message_received(line)
        else:
            print('Invalid command: {}', line)


class SsdrApiClientFactory(ClientFactory):
    def __init__(self, vita_port):
        self.vita_port = vita_port

    def startedConnecting(self, connector):
        print('Started to connect.')

    def buildProtocol(self, addr):
        print('Connected.')
        return SsdrApiProtocol(self.vita_port)

    def clientConnectionLost(self, connector, reason):
        print('Lost connection.  Reason:', reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason:', reason)
