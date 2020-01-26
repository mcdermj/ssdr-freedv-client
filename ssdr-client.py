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

if __name__ == '__main__':
    app = wx.App(False)
    reactor.registerWxApp(app)

    frame = SsdrFdvClientFrame()
    frame.Show(True)

    reactor.listenUDP(4992, SsdrDiscoveryClient(frame))
    reactor.run()
