#  This is a fix for pyinstaller.  We need to remove the
#  reactor it's already installed so that we can install
#  the proper one that works with wxwidgets.
import sys
if 'twisted.internet.reactor' in sys.modules:
    del sys.modules['twisted.internet.reactor']

from twisted.internet import wxreactor
wxreactor.install()

from twisted.internet import reactor
import wx
from ssdrframe import SsdrFdvClientFrame
from ssdrdiscovery import SsdrDiscoveryClient
import socket

if __name__ == '__main__':
    app = wx.App(False)
    reactor.registerWxApp(app)

    frame = SsdrFdvClientFrame()
    frame.Show(True)

    discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    discovery_socket.setblocking(False)
    discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    discovery_socket.bind(('0.0.0.0', 4992))

    reactor.adoptDatagramPort(discovery_socket.fileno(), socket.AF_INET, SsdrDiscoveryClient(frame))

    reactor.run()
