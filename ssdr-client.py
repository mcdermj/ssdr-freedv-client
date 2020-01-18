from twisted.internet import wxreactor

wxreactor.install()

from twisted.internet import reactor
from socket import create_connection
from pexpect.fdpexpect import fdspawn
import pprint
import wx
from sys import exit, stdout
import re
from typing import Tuple, List
# from ssdrapiclient import SsdrApiClientFactory
from vitaprotocol import VitaProtocol
from ssdrframe import SsdrFdvClientFrame

pp = pprint.PrettyPrinter(indent=4)


class ssdrclient:
    def __init__(self, addr: str, port: int) -> None:
        self.meter_list = {}
        self.sequence = 0
        self.socket = create_connection((addr, port))
        self.expect = fdspawn(self.socket.fileno(), timeout=10, encoding="utf-8", logfile=stdout)

        self.expect.expect('V(\d+\.\d+)\.(\d+\.\d+)\n')
        self.major_rev = self.expect.match.group(1)
        self.minor_rev = self.expect.match.group(2)
        print('Radio is Version {}/{}'.format(self.major_rev, self.minor_rev))

        self.expect.expect('H([0-9A-F]{8})\n')
        self.handle = self.expect.match.group(1)
        print('Our handle is {}'.format(self.handle))

    def send_command(self, command: str) -> Tuple[int, str]:
        self.expect.sendline('C{}|{}'.format(self.sequence, command))
        matcher = 'R{}\|([0-9A-Z]{{0,8}})\|(.*)\n'.format(self.sequence)
        self.expect.expect(matcher)
        self.sequence = self.sequence + 1
        return int(self.expect.match.group(1)), self.expect.match.group(2)

    def find_meter_by_name(self, name: str) -> int:
        meter_attr_re = re.compile('(\d+)\.nam={}'.format(name))

        (code, message) = self.send_command('meter list')
        if code != 0:
            return None  # XXX Exception
        for meterAttr in message.split('#'):
            match = meter_attr_re.match(meterAttr)
            if match:
                return int(match.group(1))

        return None  # XXX exception

    def subscribe_meter(self, name: str) -> None:
        id = self.find_meter_by_name(name)
        (code, message) = self.send_command('sub meter {}'.format(id))
        if code != 0:
            print("Error")

    def subscribe_meters(self, meters: List[str]) -> None:
        for meter in meters:
            self.subscribe_meter(meter)


#  XXX TODO: Need to create a discovery client to find the radio
if __name__ == '__main__':
    client = ssdrclient(addr='10.0.3.50', port=4992)
    client.subscribe_meters([
        'fdv-snr',
        'fdv-foff',
        'fdv-total-bits',
        'fdv-error-bits',
        'fdv-ber'
    ])

    vitaSocket = reactor.listenUDP(0, VitaProtocol('10.0.3.50', 4993))
    vitaPort = vitaSocket.getHost().port

    client.send_command('client udpport {}'.format(vitaSocket.getHost().port))

    # reactor.connectTCP('10.0.3.50', 4992, SsdrApiClientFactory(vitaPort))

    app = wx.App(False)
    reactor.registerWxApp(app)

    frame = SsdrFdvClientFrame()
    frame.Show(True)
    reactor.run()

    # app.MainLoop()
