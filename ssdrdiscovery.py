from vitaprotocol import VitaProtocol
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from ssdrapiclient import SsdrApiClientFactory
from ssdrframe import SsdrFdvClientFrame


class SsdrDiscoveryClient(DatagramProtocol):
    def __init__(self, frame: SsdrFdvClientFrame):
        self.radio_connected = False
        self.frame = frame

    def startProtocol(self):
        self.transport.setBroadcastAllowed(True)

    def datagramReceived(self, datagram: str, addr):
        header = VitaProtocol.parse_vita_header(datagram)
        if header['classId'] >> 32 != 0x00001c2d:
            print("This is not a flex packet, ignoring")
            return

        if header['classId'] == 0x00001c2d534cffff and header['streamId'] == 0x00000800:
            payload = VitaProtocol.parse_vita_payload(datagram).decode('utf-8').rstrip('\x00')
            attrs = {pair.split('=')[0]: pair.split('=')[1] for pair in payload.split()}
            if not self.radio_connected:
                self.radio_connected = True
                reactor.connectTCP('10.0.3.50', 4992, SsdrApiClientFactory(self.frame))
