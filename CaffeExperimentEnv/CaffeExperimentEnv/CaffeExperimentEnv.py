#coding:utf-8

import re
import wx
import subprocess as s
import os
import datetime
from stat import *
import codecs
from collections import OrderedDict

executeName = u""
dir_path = u""

prmdict = OrderedDict((
    (u"test_iter",u"100"),
    (u"test_interval",u"500"),
    (u"base_lr",u"0.01"),
    (u"momentum",u"0.9"),
    (u"weight_decay",u"0.004"),
    (u"lr_policy",u"fixed"),
    (u"display",u"100"),
    (u"max_iter",u"4000"),
    (u"snapshot",u"4000"),
    (u"snapshot_format",u"HDF5"),
    (u"snapshot_prefix",u"dir_path"),
    (u"solver_mode",u"GPU")
    ))

db_dict = { 
    u"height":"128", 
    u"width":"128"
    }

path_dict = OrderedDict((
    (u"home", [u"home dir", 0]),
    (u"image", [u"image dir", 1]),
    (u"trainlist", [u"trainlist path", 4]),
    (u"testlist", [u"testlist path", 5]),
    (u"dirpath", [u"default auto", 3]),
    (u"caffe", [u"~/caffe/build/tools", 2])
    ))


set_dir_border = 3
panel_border = 5

class prmGroup:    
    def __init__(self, dict, basepanel):
        self.value = dict
        self.base = basepanel
        self.panel = wx.Panel(basepanel, wx.ID_ANY)
        self.layout = wx.BoxSizer(wx.VERTICAL)
        # create
        self.controls = self.getPrmPanels()
        self.panel.SetSizer(self.layout)

    def getValue(self, key):
        temp = self.controls[key]
        return temp.value

    def refresh(self):
        self.panel.SetSizer(self.layout)
        
    def getPrmPanel(self,text, textbox):
        new_panel = wx.Panel(self.panel, wx.ID_ANY)
        np_layout = wx.BoxSizer(wx.HORIZONTAL)
        new_text = wx.StaticText(new_panel, wx.ID_ANY, text)
        new_textbox = wx.TextCtrl(new_panel, wx.ID_ANY, textbox, size=(100,20))
        np_layout.Add(new_text, flag = wx.EXPAND | wx.ALL, border = set_dir_border)
        np_layout.Add(new_textbox, flag = wx.EXPAND | wx.ALL, border = set_dir_border)
        new_panel.SetSizer(np_layout)
        return (new_panel, new_textbox)

    def getPrmPanels(self):
        panels = {}
        for k, v in self.value.items():
            temp = self.getPrmPanel(k, v)
            panels[k] = temp[1]
            self.layout.Add(temp[0])
        return panels

class DirGroup:
    def __init__(self, dict, basepanel, layout):
        self.value = dict
        self.base = basepanel
        self.layout = layout
        self.controls = self.getDirPanels()

    def getValue(self, key):
        temp = self.controls[key]
        return temp.value

    def setValue(self, key, val):
        temp = self.controls[key]
        temp.value = val

    def refresh(self):
        self.panel.SetSizer(self.layout)

    def getDirPanel(self, text, textbox, id):
        new_panel = wx.Panel(self.base, wx.ID_ANY)
        np_layout = wx.BoxSizer(wx.HORIZONTAL)
        new_dir_text = wx.StaticText(new_panel, wx.ID_ANY, text)
        new_dir_textbox = wx.TextCtrl(new_panel, wx.ID_ANY, textbox, size=(500,20))
        new_dir_button = wx.Button(new_panel, id, u"ref", size=(50,20))
        new_dir_button.Bind(wx.EVT_BUTTON, click_openDialog)
        np_layout.Add(new_dir_text, flag = wx.EXPAND | wx.ALL, border = set_dir_border)
        np_layout.Add(new_dir_button, flag = wx.EXPAND | wx.ALL, border = set_dir_border)
        np_layout.Add(new_dir_textbox, flag = wx.EXPAND | wx.ALL, border = set_dir_border)
        new_panel.SetSizer(np_layout)
        return (new_panel, new_dir_textbox)

    def getDirPanels(self):
        panels = {}
        for k, v in self.value.items():
            temp = self.getDirPanel(k, v[0], v[1])
            panels[k] = temp[1]
            self.layout.Add(temp[0])
        return panels


def replace(path, search, replace):
    read_file = ""
    write_file = ""
    temp_file = u"temp_file"
    search_t = search.encode('utf-8')
    replace_t = replace.encode('utf-8')
    try:
        read_file = open(path, 'r')
        write_file = open(temp_file, 'w')
        for line in read_file:
            line_t = line
            if line_t.find(search_t) != -1:
                line_t = re.sub(search_t, replace_t, line)
            write_file.write(line_t)
    finally:
        read_file.close()
        write_file.close()

    if os.path.isfile(path) and os.path.isfile(temp_file):
        os.remove(path)
        os.rename(temp_file, path)
    return 0


def editConfig():
    data = u"net: " + "\"" + os.path.join(dir_path, "quick_train_test.prototxt") + "\""
    for k, v in prmdict.items():
        if k == "lr_policy":
            data = u"%s\n" %data \
                + u"%s: \"" %k \
                + u"%s\"" %v
        elif k == "snapshot_prefix":
            data = u"%s\n" %data \
                + u"%s: \"" %k \
                + u"%s/quick\"" %dir_path
        else:
            data = u"%s\n" %data \
                + u"%s: " %k \
                + u"%s" %v

    f = open(dir_path + "/quick_solver.prototxt", "w")
    f.write(data.encode('utf-8'))
    f.close()

    replace(dir_path + "/quick.prototxt", u"dim: w", u"dim: " + db_dict["width"])
    replace(dir_path + "/quick.prototxt", u"dim: h", u"dim: " + db_dict["height"])
    replace(dir_path + "/quick_train_test.prototxt", u"mean.binaryproto", os.path.join(dir_path, u"mean.binaryproto"))
    replace(dir_path + "/quick_train_test.prototxt"
            , u"train_leveldb"
            , os.path.join(dir_path, u"train_leveldb"))
    replace(dir_path + "/quick_train_test.prototxt"
            , u"test_leveldb"
            , os.path.join(dir_path, u"test_leveldb"))

def startTime():
    global executeName
    today = datetime.datetime.today()
    executeName = "caffeGUI_ver01_" + today.strftime("%Y%m%d_%H%M%S")
    return executeName

def createConfig(path):
    p1 = "cp " + r"config/quick.prototxt" + " " + os.path.join(path, "quick.prototxt")
    print(p1)
    s.call(p1, shell = True)
    p2 = "cp " + r"config/quick_train_test.prototxt" + " " + os.path.join(path, "quick_train_test.prototxt")
    print(p2)
    s.call(p2, shell = True)
    # edit config
    editConfig()


def createDir(dir):
    global dir_path
    dir_path = os.path.join(home_Panels[1].Value, dir)
    p = "mkdir " + dir_path
    s.call(p, shell=True) # exeption > if exit
    home_Panels[1].Value = dir_path
    
    createConfig(dir_path)


def createDB(type):
    if type == "LEVELDB" or type == "LMDB":
        p1 = "%s/convert_imageset" %caffe_Panels[1].Value \
               + " -shuffle" \
               + " -backend leveldb" \
               + " -resize_height %s" %resize_Panels[0].Value \
               + " -resize_width %s" %resize_Panels[1].Value \
               + " %s/" %image_Panels[1].Value \
               + " %s" %trainlist_Panels[1].Value \
               + " %s/train_leveldb" %dir_path
        print(p1)
        s.call(p1, shell = True)
        p2 = "%s/convert_imageset" %caffe_Panels[1].Value \
               + " -shuffle" \
               + " -backend leveldb" \
               + " -resize_height %s" %resize_Panels[0].Value \
               + " -resize_width %s" %resize_Panels[1].Value \
               + " %s/" %image_Panels[1].Value \
               + " %s" %testlist_Panels[1].Value \
               + " %s/test_leveldb" %dir_path
        print(p2)
        s.call(p2, shell = True)
    else:
        wx.MessageBox("type: LEVELDB or LMDB")


def createMean():
    p = "%s/compute_image_mean" %caffe_Panels[1].Value \
           + " -backend leveldb" \
           + " %s/train_leveldb" %dir_path \
           + " %s/mean.binaryproto" %dir_path # \\ mean path
    print(p)
    s.call(p, shell = True)


def trainModel():
    p = "%s/caffe" %caffe_Panels[1].Value \
           + " train -solver" \
           + " %s/quick_solver.prototxt" %dir_path
    print(p)
    s.call(p, shell = True) # solver path

def click_button_1(event):
    global dir_path
    dir_path = dirPath_Panels[1].Value
    cmd = listbox.GetSelection()
    if cmd == 0: # createNewDir
        createDir(startTime())
    elif cmd == 1: # createDataBase
        createDB("LEVELDB")
    elif cmd == 2: # createMean
        createMean()
    elif cmd == 3: # trainModel
        trainModel()
    else: # all
        createDir(startTime())
        createDB("LEVELDB")
        createMean()
        trainModel()


def click_openDialog(event):
    result = ""
    # dir dialog
    if event.GetId() < 4:
        dlg = wx.DirDialog(None,"Choose directory","",
                       wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
    else:
        dlg = wx.FileDialog(None,"Choose file","", "","*.*")

    if dlg.ShowModal() == wx.ID_OK:
        result = dlg.GetPath() # get fullpath
    dlg.Destroy()

    id = event.GetId()

    if id == 0: # home
        dir_Controls.setValue("home", result)
    elif id == 1: # image
        dir_Controls.setValue("image", result)
    elif id == 2: # caffe
        dir_Controls.setValue("dirpath", result)
    elif id == 4: # trainlist
        dir_Controls.setValue("trainlist", result)
    elif id == 5: # testlist
        dir_Controls.setValue("testlist", result)
    elif id == 3: # dirPath
        dir_Controls.setValue("dirpath", result)





if __name__ == "__main__":
    application = wx.App()
    frame = wx.Frame(None, wx.ID_ANY, u"Caffeteria", size=(600,650))

    panel = wx.Panel(frame, wx.ID_ANY)
    layout = wx.BoxSizer(wx.VERTICAL)
    sub_panel = wx.Panel(panel, wx.ID_ANY)
    sub_layout = wx.BoxSizer(wx.HORIZONTAL)

    # button
    button_1 = wx.Button(panel, wx.ID_ANY, u"Go!", size=(50,50))
    button_1.Bind(wx.EVT_BUTTON, click_button_1)

    # controls
    dir_Controls = DirGroup(path_dict,panel,layout)
    resize_Controls = prmGroup(db_dict, sub_panel)
    prm_Controls = prmGroup(prmdict, sub_panel)

    sub_layout.Add(prm_Controls.panel)
    sub_layout.Add(resize_Controls.panel)

    # setting execute
    exec_panel = wx.Panel(resize_Controls.panel, wx.ID_ANY)
    exec_layout = wx.BoxSizer(wx.HORIZONTAL)
    element_array = (
        "createNewDir",
        "createDataBase", 
        "createMean", 
        "trainModel",
        "all")
    listbox = wx.ListBox(exec_panel, wx.ID_ANY, choices=element_array, style=wx.LB_SINGLE)  
    exec_text = wx.StaticText(exec_panel, wx.ID_ANY, u"set ExecuteMode")
    exec_layout.Add(exec_text, flag = wx.EXPAND | wx.ALL, border = set_dir_border)
    exec_layout.Add(listbox, flag = wx.EXPAND | wx.ALL, border = set_dir_border)
    exec_panel.SetSizer(exec_layout)
    resize_Controls.layout.Add(exec_panel, flag = wx.EXPAND | wx.ALL, border = panel_border)
    resize_Controls.refresh()

    # layout
    sub_panel.SetSizer(sub_layout)
    layout.Add(sub_panel, flag = wx.EXPAND | wx.ALL, border = panel_border)
    layout.Add(button_1, flag = wx.EXPAND | wx.ALL, border = panel_border)
    panel.SetSizer(layout)
    
    frame.Show()
    application.MainLoop()
