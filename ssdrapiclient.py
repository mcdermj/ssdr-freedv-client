from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineOnlyReceiver
from typing import List
from twisted.internet import reactor
from ssdrframe import SsdrFdvClientFrame
from twisted.internet.defer import Deferred, inlineCallbacks
import re


class CommandFailure(Exception):
    def __init__(self, errno: int, message: str) -> None:
        super().__init__()
        self.errno = errno
        self.message = message


class SsdrApiProtocol(LineOnlyReceiver):
    delimiter = b'\n'

    def __init__(self, frame: SsdrFdvClientFrame) -> None:
        self.minor_version = 0.0
        self.major_version = 0.0
        self.handle = 0x00
        self.sequence = 0
        self.meters = {}
        self.slices = {}
        self.frame = frame
        self.completion_list = {}
        self.response_matcher = re.compile(r'R([0-9]+)\|([0-9A-Z]{0,8})\|(.*)')
        frame.set_mode_handler(self.mode_handler)

    def mode_handler(self, event):
        mode = event.GetString()
        print("Change mode to {}".format(mode))
        for (slcno, slc) in self.slices.items():
            if slc['mode'].startswith('FDV'):
                self.send_command("slice waveform_cmd {} fdv-set-mode={}".format(slcno, mode), wait=False)

    def send_command(self, command: str) -> Deferred:
        self.sendLine('C{}|{}'.format(self.sequence, command).encode('utf-8'))
        print('Sending: "C{}|{}"'.format(self.sequence, command))
        d = Deferred()
        self.completion_list[self.sequence] = d
        self.sequence += 1
        return d

    def response_received(self, line: str) -> None:
        match = self.response_matcher.match(line)
        print('Recieved response: "{}"'.format(line))
        if match == None:
            print("Couldn't parse response line: {}".format(line))
            return

        sequence = int(match.group(1))
        errno = int(match.group(2), 16)
        message = match.group(3)

        if sequence not in self.completion_list:
            print("Couldn't find sequence {} in completion list".format(sequence))
            return

        if errno == 0:
            self.completion_list[sequence].callback(message)
        else:
            self.completion_list[sequence].errback(CommandFailure(errno, message))

    @inlineCallbacks
    def load_meters(self) -> Deferred:
        message = yield self.send_command('meter list')
        meter_attr_re = re.compile(r'(\d+)\.nam=([^#]+)')
        for match in meter_attr_re.finditer(message):
            self.meters[match.group(2)] = int(match.group(1))

    @inlineCallbacks
    def subscribe_meters(self, meters: List[str]) -> Deferred:
        if len(self.meters) == 0:
            yield self.load_meters()

        for meter in meters:
            yield self.send_command('sub meter {}'.format(self.meters[meter]))

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

    @inlineCallbacks
    def connectionMade(self) -> Deferred:
        from vitaprotocol import VitaProtocol
        vita_socket = yield reactor.listenUDP(0, VitaProtocol(self.transport.getPeer().host, 4993, self))

        yield self.send_command('client udpport {}'.format(vita_socket.getHost().port))
        yield self.send_command('sub slice all')
        yield self.subscribe_meters([
            "fdv-snr",
            "fdv-foff",
            "fdv-total-bits-lsb",
            "fdv-total-bits-msb",
            "fdv-error-bits",
            "fdv-ber",
            "fdv-clock-offset",
            "fdv-sync-quality"
        ])

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
            self.response_received(line)
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
