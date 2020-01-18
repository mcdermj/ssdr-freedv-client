import re

from twisted.internet.defer import inlineCallbacks, returnValue, Deferred
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineOnlyReceiver


class SsdrApiProtocol(LineOnlyReceiver):
    delimiter = b'\n'

    def __init__(self, vitaPort):
        self.minor_version = 0.0
        self.major_version = 0.0
        self.handle = 0x00
        self.sequence = 0
        self.pending_replies = dict()
        self.vita_port = vitaPort
        self.meters = dict()

    def meter_list_response(self, code, message):
        if int(code) != 0:
            print('Response is error, ignoring')
            return

        meter_attr_re = re.compile('(\d+)\.(.+)=(.+)')

        for meter_attr in message.split('#'):
            match = meter_attr_re.match(meter_attr)
            if match:
                (meterId, attrName, value) = match.groups()
                if meterId not in self.meters:
                    self.meters.update({meterId : {attrName: value}})
                else:
                    self.meters[meterId].update({attrName: value})

    @inlineCallbacks
    def load_meters(self):
        (code, message) = yield self.send_command('meter list')

        if int(code) != 0:
            print('Response is error, ignoring')
            return

        meter_attr_re = re.compile('(\d+)\.(.+)=(.+)')

        for meterAttr in message.split('#'):
            match = meter_attr_re.match(meterAttr)
            if match:
                (meterId, attrName, value) = match.groups()
                if meterId not in self.meters:
                    self.meters.update({meterId : {attrName: value}})
                else:
                    self.meters[meterId].update({attrName: value})

    @inlineCallbacks
    def find_meter_by_name(self, name):
        if len(self.meters) == 0:
            yield self.load_meters()

        returnValue([(meterId, entry) for (meterId, entry) in self.meters.items() if name in entry['nam']][0])

    @inlineCallbacks
    def subscribe_meter(self, name):
        (meterId, meterAttrs) = yield self.find_meter_by_name(name)
        # self.sendCommand('sub meter all')
        self.send_command('sub meter {}'.format(meterId))

    @inlineCallbacks
    def connectionMade(self):
        self.send_command('client udpport {}'.format(self.vita_port))
        yield self.subscribe_meter('fdv-snr')
        yield self.subscribe_meter('fdv-foff')
        yield self.subscribe_meter('fdv-total-bits')
        yield self.subscribe_meter('fdv-error-bits')
        yield self.subscribe_meter('fdv-ber')

    def send_command(self, command, callback=None):  # XXX Change Signature Here
        deferred = Deferred()

        self.pending_replies[self.sequence] = deferred
        line = 'C{}|{}'.format(self.sequence, command).encode()
        self.sendLine(line)
        print("Sending: {}".format(line))
        self.sequence = self.sequence + 1

        return deferred

    def version_received(self, line):
        match = re.fullmatch('V(\d+\.\d+)\.(\d+\.\d+)', line)
        if match:
            (self.major_version, self.minor_version) = match.groups()

    def handle_received(self, line):
        match = re.fullmatch('H([0-9A-Z]{8})', line)
        if match:
            self.handle = int(match.group(1), 16)

    def command_received(self, line):
        pass

    def reply_received(self, line):
        (sequence, code, message) = line.split('|')
        sequence = int(sequence[1][-1])
        print('Got reply with sequence {}, code {} and message "{}"'.format(sequence, code, message))
        if sequence in self.pending_replies:
            deferred = self.pending_replies[sequence]
            deferred.callback((code, message))
 #           self.pendingReplies[sequence](code, message)

    def status_received(self, line):
        print("Status Message: {}".format(line))

    def message_received(selfs, line):
        pass

    def lineReceived(self, line):
        line = line.decode('utf-8')
        if line[0] == 'V':
            self.version_received(line)
        elif line[0] == 'H':
            self.handle_received(line)
        elif line[0] == 'C':
            self.command_received(line)
        elif line[0] == 'R':
            self.reply_received(line)
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
