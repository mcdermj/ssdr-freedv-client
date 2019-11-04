from twisted.internet import reactor
import pprint

from ssdrapiclient import SsdrApiClientFactory
from vitaprotocol import VitaProtocol

pp = pprint.PrettyPrinter(indent=4)

#  XXX TODO: Need to create a discovery client to find the radio

if __name__ == '__main__':
    vitaSocket = reactor.listenUDP(0, VitaProtocol('10.0.3.50', 4993))
    vitaPort = vitaSocket.getHost().port

    reactor.connectTCP('10.0.3.50', 4992, SsdrApiClientFactory(vitaPort))

    reactor.run()