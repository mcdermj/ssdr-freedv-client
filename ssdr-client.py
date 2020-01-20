from twisted.internet import wxreactor
wxreactor.install()

from twisted.internet import reactor
import wx
from ssdrapiclient import SsdrApiClientFactory
from ssdrframe import SsdrFdvClientFrame


#  XXX TODO: Need to create a discovery client to find the radio
if __name__ == '__main__':
    app = wx.App(False)
    reactor.registerWxApp(app)

    frame = SsdrFdvClientFrame()
    frame.Show(True)

    reactor.connectTCP('10.0.3.50', 4992, SsdrApiClientFactory(frame))

    reactor.run()
