import re
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineOnlyReceiver
from pexpect.fdpexpect import fdspawn
from sys import stdout
from typing import Tuple, List, Optional
from twisted.internet import reactor
from ssdrframe import SsdrFdvClientFrame


class SsdrApiProtocol(LineOnlyReceiver):
    delimiter = b'\n'

    def __init__(self, frame: SsdrFdvClientFrame) -> None:
        self.minor_version = 0.0
        self.major_version = 0.0
        self.handle = 0x00
        self.sequence = 0
        self.vita_port = 0
        self.meters = {}
        self.major_rev = 0
        self.minor_rev = 0
        self.handle = None
        self.expect = None
        self.freedv_slice = None
        self.slices = {}
        self.vita_socket = None
        self.frame = frame

        frame.set_mode_handler(self.mode_handler)

    def mode_handler(self, event):
        mode = event.GetString()
        print("Change mode to {}".format(mode))
        for (slcno, slc) in self.slices.items():
            if slc['mode'].startswith('FDV'):
                self.send_command("slice waveform_cmd {} fdv-set-mode={}".format(slcno, mode), wait=False)

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
            self.meters[match.group(2)] = int(match.group(1))

    def subscribe_meters(self, meters: List[str]) -> None:
        if len(self.meters) == 0:
            self.load_meters()

        for meter in meters:
            (code, message) = self.send_command('sub meter {}'.format(self.meters[meter]))
            if code != 0:
                print("Error subscribing meter {}({})".format(meter, self.meters[meter]))

    def update_meter(self, meter_id: int, meter_value: int):
        for (k, v) in self.meters.items():
            if v == meter_id:
                method_name = k.replace('-', '_')
                if method_name.startswith('fdv_'):
                    method_name = method_name[4:]
                if hasattr(self.frame, method_name):
                    setattr(self.frame, method_name, meter_value)

    def update_settings(self):
        for (slcno, slc) in self.slices.items():
            if slc['mode'].startswith('FDV') and 'fdv-mode' in slc:
                self.frame.mode = slc['fdv-mode']

    def connectionMade(self) -> None:
        from vitaprotocol import VitaProtocol

        self.vita_socket = reactor.listenUDP(0, VitaProtocol(self.transport.getPeer().host, 4993, self))
        self.vita_port = self.vita_socket.getHost().port

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
            "fdv-total-bits-lsb",
            "fdv-total-bits-msb",
            "fdv-error-bits",
            "fdv-ber",
            "fdv-clock-offset",
            "fdv-sync-quality"
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
                try:
                    (name, value) = token.split('=')
                except ValueError:
                    self.slices[sliceno][token] = ''
                else:
                    self.slices[sliceno][name] = value
            self.update_settings()

    def message_received(self, line):
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
    def __init__(self, frame: SsdrFdvClientFrame):
        self.frame = frame

    def startedConnecting(self, connector):
        print('Started to connect.')

    def buildProtocol(self, addr):
        print('Connected.')
        return SsdrApiProtocol(self.frame)

    def clientConnectionLost(self, connector, reason):
        print('Lost connection.  Reason:', reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason:', reason)
