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
   # (u"gamma",u"0.0001"),
   # (u"power",u"0.75"),
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


set_dir_border = 3
panel_border = 5


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
            data = data + u"\n" + k + u": \"" + v + "\""
        elif k == "snapshot_prefix":
            data = data + u"\n" + k + u": \"" + dir_path + "\""
        else:
            data = data + u"\n" + k + u": " + v
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
    s.call("cp "
        + r"config/quick.prototxt" # \ > /
        + " " + os.path.join(path, "quick.prototxt")
        , shell = True # for win
        )
    s.call("cp "
        + r"config/quick_train_test.prototxt" # \ > /
        + " " + os.path.join(path, "quick_train_test.prototxt")
        , shell = True # for win
        )
    # edit config
    editConfig()


def createDir(dir):
    global dir_path
    dir_path = os.path.join(home_Panels[1].Value, dir)
    s.call("mkdir " + dir_path
           , shell=True # for win
           ) # exeption > if exit
    home_Panels[1].Value = dir_path
    
    createConfig(dir_path)


def createDB(type):
    if type == "LEVELDB" or type == "LMDB":
        s.call(caffe_Panels[1].Value + "/" + "convert_imageset "  # \\
               + image_Panels[1].Value + "/ " # image root
               + trainlist_Panels[1].Value + " " # train list
               + dir_path + "/" + "train_leveldb"
               + " -shuffle "
               + " -backend leveldb" 
               + " -resize_height " + resize_Panels[0].Value
               + " -resize_width " + resize_Panels[1].Value
               , shell = True
               ) # wait process end ??
        s.call(caffe_Panels[1].Value + "/" + "convert_imageset "  # \\
               + image_Panels[1].Value + "/ " # image root
               + testlist_Panels[1].Value + " " # test list
               + dir_path + "/" + "test_leveldb" 
               + " -shuffle "
               + " -backend leveldb" 
               + " -resize_height " + resize_Panels[0].Value
               + " -resize_width " + resize_Panels[1].Value
               , shell = True
               ) # wait process end ??
    else:
        wx.MessageBox("type: LEVELDB or LMDB")


def createMean():
    print(caffe_Panels[1].Value + "/" + "compute_image_mean" # \\
           + " -backend leveldb "
           + dir_path + "/" + "train_leveldb " # db root
           + dir_path + "/" + "mean.binaryproto" # \\ mean path
           )
    s.call(caffe_Panels[1].Value + "/" + "compute_image_mean" # \\
           + " -backend leveldb "
           + dir_path + "/" + "train_leveldb " # db root
           + dir_path + "/" + "mean.binaryproto" # \\ mean path
           , shell = True
           )


def trainModel():
    s.call(caffe_Panels[1].Value + "/" + "caffe" # \\
           + " train -solver "
           + dir_path + "/quick_solver.prototxt"
           , shell = True
           ) # solver path

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
        home_Panels[1].Value = result
    elif id == 1: # image
        image_Panels[1].Value = result
    elif id == 2: # caffe
        caffe_Panels[1].Value = result
    elif id == 4: # trainlist
        trainlist_Panels[1].Value = result
    elif id == 5: # testlist
        testlist_Panels[1].Value = result
    elif id == 3: # dirPath
        dirPath_Panels[1].Value = result

def getDirPanel(panel, text, textbox, id):
    new_panel = wx.Panel(panel, wx.ID_ANY)
    np_layout = wx.BoxSizer(wx.HORIZONTAL)
    
    new_dir_text = wx.StaticText(new_panel, wx.ID_ANY, text)
    new_dir_textbox = wx.TextCtrl(new_panel, wx.ID_ANY, textbox
                                   , size=(500,20))
    new_dir_button = wx.Button(new_panel, id, u"ref", size=(50,20))
    new_dir_button.Bind(wx.EVT_BUTTON, click_openDialog)
    
    np_layout.Add(new_dir_text, flag = wx.EXPAND | wx.ALL, border = set_dir_border)
    np_layout.Add(new_dir_button, flag = wx.EXPAND | wx.ALL, border = set_dir_border)
    np_layout.Add(new_dir_textbox, flag = wx.EXPAND | wx.ALL, border = set_dir_border)

    new_panel.SetSizer(np_layout)

    return (new_panel, new_dir_textbox)


def getPrmPanel(panel, text, textbox):
    new_panel = wx.Panel(panel, wx.ID_ANY)
    np_layout = wx.BoxSizer(wx.HORIZONTAL)

    new_text = wx.StaticText(new_panel, wx.ID_ANY, text)
    new_textbox = wx.TextCtrl(new_panel, wx.ID_ANY, textbox
                              , size=(100,20))

    np_layout.Add(new_text, flag = wx.EXPAND | wx.ALL, border = set_dir_border)
    np_layout.Add(new_textbox, flag = wx.EXPAND | wx.ALL, border = set_dir_border)

    new_panel.SetSizer(np_layout)
    return (new_panel, new_textbox)


def getPrmPanels(prmdict, panel, prm_panel, prm_layout):
    panels = []
    for k, v in prmdict.items():
        temp = getPrmPanel(prm_panel, k, v)
        panels.append(temp[1])
        prm_layout.Add(temp[0])
    prm_panel.SetSizer(prm_layout)
    return panels



if __name__ == "__main__":
    application = wx.App()
    frame = wx.Frame(None, wx.ID_ANY, u"Test", size=(600,650))
    
    # main panel
    panel = wx.Panel(frame, wx.ID_ANY)
    #panel.SetBackgroundColour("#FFFFFFF")
    layout = wx.BoxSizer(wx.VERTICAL)

    sub_panel = wx.Panel(panel, wx.ID_ANY)
    sub_layout = wx.BoxSizer(wx.HORIZONTAL)

    # button
    button_1 = wx.Button(panel, wx.ID_ANY, u"Go!", size=(50,50))
    button_1.Bind(wx.EVT_BUTTON, click_button_1)

    # setting path
    home_Panels = getDirPanel(panel, u"home", u"home dir", 0)
    image_Panels = getDirPanel(panel, u"image", u"image dir", 1)
    trainlist_Panels = getDirPanel(panel, u"trainlist", u"trainlist path", 4)
    testlist_Panels = getDirPanel(panel, u"testlist", u"testlist path", 5)
    dirPath_Panels = getDirPanel(panel, u"dirpath", u"default auto", 3)
    caffe_Panels = getDirPanel(panel, u"caffe", u"~/caffe/build/tools", 2)

    # setting resize
    resize_panel = wx.Panel(sub_panel, wx.ID_ANY)
    resize_layout = wx.BoxSizer(wx.VERTICAL)
    resize_Panels = getPrmPanels(db_dict, panel, resize_panel, resize_layout)

    # setting prm
    prm_panel = wx.Panel(sub_panel, wx.ID_ANY)
    prm_layout = wx.BoxSizer(wx.VERTICAL)
    prm_Panels = getPrmPanels(prmdict, panel, prm_panel, prm_layout)


    # setting execute
    exec_panel = wx.Panel(resize_panel, wx.ID_ANY)
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
    
    resize_layout.Add(exec_panel, flag = wx.EXPAND | wx.ALL, border = panel_border)
    resize_panel.SetSizer(resize_layout)

    #layout
    layout.Add(home_Panels[0], flag = wx.EXPAND | wx.ALL, border = panel_border)
    layout.Add(image_Panels[0], flag = wx.EXPAND | wx.ALL, border = panel_border)
    layout.Add(trainlist_Panels[0], flag = wx.EXPAND | wx.ALL, border = panel_border)
    layout.Add(testlist_Panels[0], flag = wx.EXPAND | wx.ALL, border = panel_border)
    layout.Add(dirPath_Panels[0], flag = wx.EXPAND | wx.ALL, border = panel_border)
    layout.Add(caffe_Panels[0], flag = wx.EXPAND | wx.ALL, border = panel_border)
    sub_layout.Add(prm_panel, flag = wx.EXPAND | wx.ALL, border = panel_border)
    sub_layout.Add(resize_panel, flag = wx.EXPAND | wx.ALL, border = panel_border)

    sub_panel.SetSizer(sub_layout)
    layout.Add(sub_panel, flag = wx.EXPAND | wx.ALL, border = panel_border)
    layout.Add(button_1, flag = wx.EXPAND | wx.ALL, border = panel_border)

    panel.SetSizer(layout)
    frame.Show()
    application.MainLoop()
