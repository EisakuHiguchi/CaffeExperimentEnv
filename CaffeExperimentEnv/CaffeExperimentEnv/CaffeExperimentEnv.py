import wx
import subprocess as s

application = wx.App()
frame = wx.Frame(None, wx.ID_ANY, u"Test", size=(300,300))

panel = wx.Panel(frame, wx.ID_ANY)
panel.SetBackgroundColour("#AFAFAF")

# button
button_1 = wx.Button(panel, wx.ID_ANY, u"Go!")
# slider
slider = wx.Slider(panel,style=wx.SL_HORIZONTAL)
# text
text_1 = wx.TextCtrl(panel, wx.ID_ANY, u"attribute1")
# label
text_s1 = wx.StaticText(panel, wx.ID_ANY, u"s_attribute")

layout = wx.BoxSizer(wx.VERTICAL)
layout.Add(button_1)
layout.Add(slider)
layout.Add(text_1)
layout.Add(text_s1)

panel.SetSizer(layout)

s.call("dir",shell=True)

frame.Show()

application.MainLoop()
