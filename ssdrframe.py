import wx

class SsdrFdvClientFrame (wx.Frame):
    def __init__(self):
        super().__init__(None, wx.ID_ANY, "SmartSDR FreeDV Waveform Control")

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT))
        # this->SetSizeHints(wxDefaultSize, wxDefaultSize);
        # this->SetForegroundColour(wxSystemSettings::GetColour(wxSYS_COLOUR_WINDOWTEXT));
        # this->SetBackgroundColour(wxSystemSettings::GetColour(wxSYS_COLOUR_3DLIGHT));
        # this->SetSizeHints(wxDefaultSize, wxDefaultSize);
        # this->SetForegroundColour(wxSystemSettings::GetColour(wxSYS_COLOUR_WINDOWTEXT));
        # this->SetBackgroundColour(wxSystemSettings::GetColour(wxSYS_COLOUR_3DLIGHT));

        self.box_sizer = wx.BoxSizer(wx.VERTICAL)
        self.snr_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, 'SNR'), wx.VERTICAL)
        self.gauge_snr = wx.Gauge(self, wx.ID_ANY, 25, wx.DefaultPosition, wx.Size(15, 135), wx.GA_SMOOTH | wx.GA_VERTICAL)
        self.gauge_snr.SetToolTip('Displays signal to noise ratio in dB.')
        self.snr_sizer.Add(self.gauge_snr, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)

        self.text_snr = wx.StaticText(self, wx.ID_ANY, ' 0.0', wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER)
        self.snr_sizer.Add(self.text_snr, 0, wx.ALIGN_CENTER_HORIZONTAL, 1)

        self.checkbox_snr = wx.CheckBox(self, wx.ID_ANY, "Slow", wx.DefaultPosition, wx.DefaultSize, wx.CHK_2STATE)
        self.checkbox_snr.SetToolTip('Smooth but slow SNR estimation')
        self.snr_sizer.Add(self.checkbox_snr, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.box_sizer.Add(self.snr_sizer, 2, wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND, 1)

        self.sbsizer3_33 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Sync"), wx.VERTICAL)
        self.text_sync = wx.StaticText(self, wx.ID_ANY, "Modem", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER)
        self.sbsizer3_33.Add(self.text_sync, 0, wx.ALIGN_CENTER_HORIZONTAL, 1)

        self.text_interleaver_sync = wx.StaticText(self, wx.ID_ANY, "Interleaver", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER)
        self.sbsizer3_33.Add(self.text_interleaver_sync, 0, wx.ALIGN_CENTER_HORIZONTAL, 1)
        self.text_sync.Disable()

        self.btn_resync = wx.Button(self, wx.ID_ANY, "ReSync", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER)
        self.sbsizer3_33.Add(self.btn_resync, 0, wx.ALIGN_CENTER, 1)
        self.text_interleaver_sync.Disable()

        self.box_sizer.Add(self.sbsizer3_33, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL | wx.EXPAND, 3)

        self.ber_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, 'Stats'), wx.VERTICAL)
        self.btn_ber_reset = wx.Button(self, wx.ID_ANY, "Reset", wx.DefaultPosition, wx.DefaultSize, 0)
        self.ber_sizer.Add(self.btn_ber_reset, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)

        self.text_bits = wx.StaticText(self, wx.ID_ANY, 'Bits: 0', wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT)
        self.ber_sizer.Add(self.text_bits, 0, wx.ALIGN_LEFT, 1)

        self.text_errors = wx.StaticText(self, wx.ID_ANY, 'Errs: 0', wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT)
        self.ber_sizer.Add(self.text_errors, 0, wx.ALIGN_LEFT, 1)

        self.text_ber = wx.StaticText(self, wx.ID_ANY, 'BER: 0', wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT)
        self.ber_sizer.Add(self.text_ber, 0, wx.ALIGN_LEFT, 1)

        self.text_resyncs = wx.StaticText(self, wx.ID_ANY, 'Resyncs: 0', wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT)
        self.ber_sizer.Add(self.text_resyncs, 0, wx.ALIGN_LEFT, 1)

        self.text_clkoff = wx.StaticText(self, wx.ID_ANY, 'ClkOff: 0', wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT)
        self.ber_sizer.Add(self.text_clkoff, 0, wx.ALIGN_LEFT, 1)

        self.text_freqoff = wx.StaticText(self, wx.ID_ANY, 'FreqOff: 0', wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT)
        self.ber_sizer.Add(self.text_freqoff, 0, wx.ALIGN_LEFT, 1)

        self.text_sync_metric = wx.StaticText(self, wx.ID_ANY, 'Sync: 0', wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT)
        self.ber_sizer.Add(self.text_sync_metric, 0, wx.ALIGN_LEFT, 1)

        self.text_codec2_var = wx.StaticText(self, wx.ID_ANY, 'Var: 0', wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_LEFT)
        self.ber_sizer.Add(self.text_codec2_var, 0, wx.ALIGN_LEFT, 1)

        self.box_sizer.Add(self.ber_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL | wx.EXPAND, 3)

        self.level_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, "Level"), wx.VERTICAL)

        self.text_level = wx.StaticText(self, wx.ID_ANY, "", wx.DefaultPosition, wx.Size(60, -1), wx.ALIGN_CENTER)
        self.text_level.SetForegroundColour(wx.Colour(255, 0, 0))
        self.level_sizer.Add(self.text_level, 0, wx.ALIGN_LEFT, 1)

        self.gauge_level = wx.Gauge(self, wx.ID_ANY, 100, wx.DefaultPosition, wx.Size(15, 135), wx.GA_SMOOTH | wx.GA_VERTICAL)
        self.gauge_level.SetToolTip('Peak of From Radio in Rx, or peak of From Mic in Tx mode.  If Red you should reduce your levels')
        self.level_sizer.Add(self.gauge_level, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10);

        self.box_sizer.Add(self.level_sizer, 2, wx.ALIGN_CENTER | wx.ALL | wx.EXPAND, 1)


        self.SetSizer(self.box_sizer)

    @property
    def freq_offset(self) -> None:
        return self.text_freqoff.GetLabelText()

    @freq_offset.setter
    def freq_offset(self, offset: float) -> None:
        self.text_freqoff.SetLabelText("FreqOff: {}".format(offset))
