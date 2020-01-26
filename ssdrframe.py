import wx
from typing import Callable


class SsdrFdvClientFrame (wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title=u"SmartSDR FreeDV Waveform Control", pos=wx.DefaultPosition,
                          size=wx.Size(250, 500),
                          style=wx.CLOSE_BOX | wx.DEFAULT_FRAME_STYLE | wx.FRAME_NO_TASKBAR | wx.TAB_TRAVERSAL)

        self.SetSizeHints(wx.Size(250, 500), wx.Size(250, 500))

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.snr_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"SNR"), wx.VERTICAL)

        self.gauge_snr = wx.Gauge(self.snr_sizer.GetStaticBox(), wx.ID_ANY, 25, wx.DefaultPosition, wx.Size(15, 135),
                                  wx.GA_SMOOTH | wx.GA_VERTICAL)
        self.gauge_snr.SetValue(0)
        self.gauge_snr.SetMinSize(wx.Size(15, 135))
        self.gauge_snr.SetMaxSize(wx.Size(15, 135))

        self.snr_sizer.Add(self.gauge_snr, 1, wx.ALL | wx.FIXED_MINSIZE | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.text_snr = wx.StaticText(self.snr_sizer.GetStaticBox(), wx.ID_ANY, u"0.00", wx.DefaultPosition, wx.DefaultSize,
                                      wx.ALIGN_CENTER_HORIZONTAL | wx.ST_NO_AUTORESIZE)
        self.text_snr.Wrap(-1)

        self.snr_sizer.Add(self.text_snr, 0, wx.ALIGN_BOTTOM | wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        self.main_sizer.Add(self.snr_sizer, 1, wx.ALL | wx.EXPAND, 5)

        self.stats_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"Stats"), wx.VERTICAL)

        bSizer5 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText2 = wx.StaticText(self.stats_sizer.GetStaticBox(), wx.ID_ANY, u"Bits:", wx.DefaultPosition,
                                           wx.DefaultSize, wx.ALIGN_LEFT)
        self.m_staticText2.Wrap(-1)

        bSizer5.Add(self.m_staticText2, 0, wx.ALIGN_LEFT | wx.BOTTOM, 5)

        self.text_bits = wx.StaticText(self.stats_sizer.GetStaticBox(), wx.ID_ANY, u"0", wx.DefaultPosition,
                                       wx.DefaultSize, wx.ALIGN_RIGHT)
        self.text_bits.Wrap(-1)

        bSizer5.Add(self.text_bits, 1, wx.BOTTOM, 5)

        self.stats_sizer.Add(bSizer5, 1, wx.EXPAND, 5)

        bSizer6 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText4 = wx.StaticText(self.stats_sizer.GetStaticBox(), wx.ID_ANY, u"Errors:", wx.DefaultPosition,
                                           wx.DefaultSize, wx.ALIGN_LEFT)
        self.m_staticText4.Wrap(-1)

        bSizer6.Add(self.m_staticText4, 0, wx.ALIGN_LEFT | wx.BOTTOM, 5)

        self.text_errors = wx.StaticText(self.stats_sizer.GetStaticBox(), wx.ID_ANY, u"0", wx.DefaultPosition,
                                         wx.DefaultSize, wx.ALIGN_RIGHT)
        self.text_errors.Wrap(-1)

        bSizer6.Add(self.text_errors, 1, wx.ALIGN_RIGHT | wx.BOTTOM, 5)

        self.stats_sizer.Add(bSizer6, 1, wx.EXPAND, 5)

        bSizer7 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText6 = wx.StaticText(self.stats_sizer.GetStaticBox(), wx.ID_ANY, u"BER", wx.DefaultPosition,
                                           wx.DefaultSize, wx.ALIGN_LEFT)
        self.m_staticText6.Wrap(-1)

        bSizer7.Add(self.m_staticText6, 0, wx.ALIGN_LEFT | wx.BOTTOM, 5)

        self.text_ber = wx.StaticText(self.stats_sizer.GetStaticBox(), wx.ID_ANY, u"0.00", wx.DefaultPosition,
                                      wx.DefaultSize, wx.ALIGN_RIGHT)
        self.text_ber.Wrap(-1)

        bSizer7.Add(self.text_ber, 1, wx.ALIGN_RIGHT | wx.BOTTOM, 5)

        self.stats_sizer.Add(bSizer7, 1, wx.EXPAND, 5)

        bSizer8 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText8 = wx.StaticText(self.stats_sizer.GetStaticBox(), wx.ID_ANY, u"Clock Offset", wx.DefaultPosition,
                                           wx.DefaultSize, wx.ALIGN_LEFT)
        self.m_staticText8.Wrap(-1)

        bSizer8.Add(self.m_staticText8, 0, wx.ALIGN_LEFT | wx.BOTTOM, 5)

        self.text_clkoff = wx.StaticText(self.stats_sizer.GetStaticBox(), wx.ID_ANY, u"0.00", wx.DefaultPosition,
                                         wx.DefaultSize, wx.ALIGN_RIGHT)
        self.text_clkoff.Wrap(-1)

        bSizer8.Add(self.text_clkoff, 1, wx.ALIGN_RIGHT | wx.BOTTOM, 5)

        self.stats_sizer.Add(bSizer8, 1, wx.EXPAND, 5)

        bSizer9 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText10 = wx.StaticText(self.stats_sizer.GetStaticBox(), wx.ID_ANY, u"Frequency Offset:",
                                            wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT)
        self.m_staticText10.Wrap(-1)

        bSizer9.Add(self.m_staticText10, 0, wx.ALIGN_LEFT | wx.BOTTOM, 5)

        self.text_freqoff = wx.StaticText(self.stats_sizer.GetStaticBox(), wx.ID_ANY, u"0.0", wx.DefaultPosition,
                                          wx.DefaultSize, wx.ALIGN_RIGHT)
        self.text_freqoff.Wrap(-1)

        bSizer9.Add(self.text_freqoff, 1, wx.ALIGN_RIGHT | wx.BOTTOM, 5)

        self.stats_sizer.Add(bSizer9, 1, wx.EXPAND, 5)

        bSizer10 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText12 = wx.StaticText(self.stats_sizer.GetStaticBox(), wx.ID_ANY, u"Sync:", wx.DefaultPosition,
                                            wx.DefaultSize, wx.ALIGN_LEFT)
        self.m_staticText12.Wrap(-1)

        bSizer10.Add(self.m_staticText12, 0, wx.ALIGN_LEFT | wx.BOTTOM, 5)

        self.text_sync_metric = wx.StaticText(self.stats_sizer.GetStaticBox(), wx.ID_ANY, u"0.00", wx.DefaultPosition,
                                              wx.DefaultSize, wx.ALIGN_RIGHT)
        self.text_sync_metric.Wrap(-1)

        bSizer10.Add(self.text_sync_metric, 1, wx.ALIGN_RIGHT | wx.BOTTOM, 5)

        self.stats_sizer.Add(bSizer10, 1, wx.EXPAND, 5)

        self.main_sizer.Add(self.stats_sizer, 0, wx.EXPAND | wx.ALL, 5)

        sbSizer6 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"Control"), wx.VERTICAL)

        bSizer11 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText14 = wx.StaticText(sbSizer6.GetStaticBox(), wx.ID_ANY, u"Mode", wx.DefaultPosition,
                                            wx.DefaultSize, 0)
        self.m_staticText14.Wrap(-1)

        bSizer11.Add(self.m_staticText14, 1, wx.ALIGN_LEFT | wx.ALL | wx.EXPAND, 5)

        mode_selectorChoices = [u"700C", u"700D", u"800XA", u"1600"]
        self.mode_selector = wx.Choice(sbSizer6.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
                                       mode_selectorChoices, 0)
        self.mode_selector.SetSelection(0)
        bSizer11.Add(self.mode_selector, 0, wx.ALIGN_RIGHT | wx.ALL | wx.EXPAND, 5)

        sbSizer6.Add(bSizer11, 1, wx.EXPAND, 5)

        self.main_sizer.Add(sbSizer6, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 5)

        self.SetSizer(self.main_sizer)
        self.Layout()

        self.Centre(wx.BOTH)

        self.total_bits = 0

    @property
    def foff(self) -> str:
        return self.text_freqoff.GetLabelText()

    @foff.setter
    def foff(self, offset: int) -> None:
        offset /= 1 << 6
        self.text_freqoff.SetLabelText("{:.1f}".format(offset))
        self.text_freqoff.InvalidateBestSize()

    @property
    def snr(self) -> str:
        return self.text_snr.GetLabelText()

    @snr.setter
    def snr(self, snr: float) -> None:
        snr /= 1 << 6
        self.text_snr.SetLabel('{:.2f}'.format(snr))
        self.text_snr.InvalidateBestSize()
        self.snr_sizer.Layout()
        self.gauge_snr.SetValue(snr)

    @property
    def mode(self) -> str:
        return self.mode_selector.GetStringSelection()

    @mode.setter
    def mode(self, mode: str) -> None:
        self.mode_selector.SetStringSelection(mode)

    @property
    def ber(self) -> str:
        return self.text_ber.GetLabelText()

    @ber.setter
    def ber(self, ber: int) -> None:
        ber /= 1 << 6
        self.text_ber.SetLabel('{:.2f}'.format(ber))
        self.text_ber.InvalidateBestSize()

    @property
    def clock_offset(self) -> str:
        return self.text_clkoff.GetLabelText()

    @clock_offset.setter
    def clock_offset(self, offset: int) -> None:
        offset /= 1 << 6
        self.text_clkoff.SetLabel('{:.2f}'.format(offset))
        self.text_clkoff.InvalidateBestSize()

    @property
    def sync_quality(self) -> str:
        return self.text_sync_metric.GetLabelText()

    @sync_quality.setter
    def sync_quality(self, quality: int) -> None:
        quality /= 1 << 6
        self.text_sync_metric.SetLabel('{:.2f}'.format(quality))
        self.text_sync_metric.InvalidateBestSize()

    @property
    def total_bits_msb(self) -> int:
        return self.text_bits.GetLabelText()

    @total_bits_msb.setter
    def total_bits_msb(self, bits: int) -> None:
        self.total_bits = (self.total_bits & 0x0000ffff) + ((bits & 0xffff) << 16)
        self.text_bits.SetLabel('{}'.format(self.total_bits))
        self.text_bits.InvalidateBestSize()

    @property
    def total_bits_lsb(self) -> int:
        return self.text_bits.GetLabelText()

    @total_bits_lsb.setter
    def total_bits_lsb(self, bits: int) -> None:
        self.total_bits = (self.total_bits & 0xffff0000) + (bits & 0xffff)
        self.text_bits.SetLabel('{}'.format(self.total_bits))
        self.text_bits.InvalidateBestSize()

    @property
    def error_bits(self) -> str:
        return self.text_errors.GetLabelText()

    @error_bits.setter
    def error_bits(self, bits: int) -> None:
        bits &= 0xffff
        self.text_errors.SetLabel('{}'.format(bits))
        self.text_errors.InvalidateBestSize()

    def set_mode_handler(self, handler: Callable):
        self.Bind(wx.EVT_CHOICE, handler, self.mode_selector)
