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
