import re

from twisted.internet.defer import inlineCallbacks, returnValue, Deferred
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineOnlyReceiver


class SsdrApiProtocol(LineOnlyReceiver):
    delimiter = b'\n'

    def __init__(self, vitaPort):
        self.minorVersion = 0.0
        self.majorVersion = 0.0
        self.handle = 0x00
        self.sequence = 0
        self.pendingReplies = dict()
        self.vitaPort = vitaPort
        self.meters = dict()

    def meterListResponse(self, code, message):
        if int(code) != 0:
            print('Response is error, ignoring')
            return

        meterAttrRe = re.compile('(\d+)\.(.+)=(.+)')

        for meterAttr in message.split('#'):
            match = meterAttrRe.match(meterAttr)
            if match:
                (meterId, attrName, value) = match.groups()
                if meterId not in self.meters:
                    self.meters.update({meterId : {attrName: value}})
                else:
                    self.meters[meterId].update({attrName: value})

    @inlineCallbacks
    def loadMeters(self):
        (code, message) = yield self.sendCommand('meter list')

        if int(code) != 0:
            print('Response is error, ignoring')
            return

        meterAttrRe = re.compile('(\d+)\.(.+)=(.+)')

        for meterAttr in message.split('#'):
            match = meterAttrRe.match(meterAttr)
            if match:
                (meterId, attrName, value) = match.groups()
                if meterId not in self.meters:
                    self.meters.update({meterId : {attrName: value}})
                else:
                    self.meters[meterId].update({attrName: value})

    @inlineCallbacks
    def findMeterByName(self, name):
        if len(self.meters) == 0:
            yield self.loadMeters()

        returnValue([(meterId, entry) for (meterId, entry) in self.meters.items() if name in entry['nam']][0])

    @inlineCallbacks
    def subscribeMeter(self, name):
        (meterId, meterAttrs) = yield self.findMeterByName(name)
        # self.sendCommand('sub meter all')
        self.sendCommand('sub meter {}'.format(meterId))

    @inlineCallbacks
    def connectionMade(self):
        self.sendCommand('client udpport {}'.format(self.vitaPort))
        yield self.subscribeMeter('fdv-snr')
        yield self.subscribeMeter('fdv-foff')
        yield self.subscribeMeter('fdv-total-bits')
        yield self.subscribeMeter('fdv-error-bits')
        yield self.subscribeMeter('fdv-ber')


    def sendCommand(self, command, callback=None):  # XXX Change Signature Here
        deferred = Deferred()

        self.pendingReplies[self.sequence] = deferred
        line = 'C{}|{}'.format(self.sequence, command).encode()
        self.sendLine(line)
        print("Sending: {}".format(line))
        self.sequence = self.sequence + 1

        return deferred

    def versionReceived(self, line):
        match = re.fullmatch('V(\d+\.\d+)\.(\d+\.\d+)', line)
        if match:
            (self.majorVersion, self.minorVersion) = match.groups()

    def handleReceived(self, line):
        match = re.fullmatch('H([0-9A-Z]{8})', line)
        if match:
            self.handle = int(match.group(1), 16)

    def commandReceived(self, line):
        pass

    def replyReceived(self, line):
        (sequence, code, message) = line.split('|')
        sequence = int(sequence[1][-1])
        print('Got reply with sequence {}, code {} and message "{}"'.format(sequence, code, message))
        if sequence in self.pendingReplies:
            deferred = self.pendingReplies[sequence]
            deferred.callback((code, message))
 #           self.pendingReplies[sequence](code, message)

    def statusReceived(self, line):
        print("Status Message: {}".format(line))

    def messageReceived(selfs, line):
        pass

    def lineReceived(self, line):
        line = line.decode('utf-8')
        if line[0] == 'V':
            self.versionReceived(line)
        elif line[0] == 'H':
            self.handleReceived(line)
        elif line[0] == 'C':
            self.commandReceived(line)
        elif line[0] == 'R':
            self.replyReceived(line)
        elif line[0] == 'S':
            self.statusReceived(line)
        elif line[0] == 'M':
            self.messageReceived(line)
        else:
            print('Invalid command: {}', line)


class SsdrApiClientFactory(ClientFactory):
    def __init__(self, vitaPort):
        self.vitaPort = vitaPort

    def startedConnecting(self, connector):
        print('Started to connect.')

    def buildProtocol(self, addr):
        print('Connected.')
        return SsdrApiProtocol(self.vitaPort)

    def clientConnectionLost(self, connector, reason):
        print('Lost connection.  Reason:', reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason:', reason)