import wx
import subprocess as s
import os
import datetime
from stat import *

executeName = u""
dir_path = u""

set_dir_border = 3
panel_border = 5

def startTime():
    global executeName
    today = datetime.datetime.today()
    executeName = "caffeGUI_ver01_" + today.strftime("%Y%m%d_%H%M%S")
    return executeName

def createConfig(path):
    s.call("copy "
        + r"config\config_test.txt" # \ > /
        + " " + os.path.join(path, "config_test.txt")
        , shell = True # for win
        ) # \ > /
    # edit config


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
        s.call(caffe_Panels[1].Value + "\\" + "convert_imageset "  # \\
               + dir_path + " " # image root
               + trainlist_Panels[1].Value + " " # train list
               + executeName + "_train" # 
               + " -shuffle "
               + " -backend leveldb" 
               + " -resize_height " + resize_Panels[0].Value
               + " -resize_width " + resize_Panels[1].Value
               ) # wait process end ??
        s.call(caffe_Panels[1].Value + "\\" + "convert_imageset "  # \\
               + dir_path + " " # image root
               + test_list_path + " " # test list
               + testlist_Panels[1].Value + "_test" # 
               + " -shuffle "
               + " -backend leveldb" 
               + " -resize_height " + resize_Panels[0].Value
               + " -resize_width " + resize_Panels[1].Value
               )
    else:
        wx.MessageBox("type: LEVELDB or LMDB")


def createMean():
    s.call(caffe_Panels[1].Value + "\\" + "compute_image_mean " # \\
           + dir_path + " " # db root
           + dir_path + "\\" + "mean.binarypoto" # \\ mean path
           + " -backend leveldb")


def trainModel():
    s.call(caffe_Panels[1].Value + "\\" + "caffe" # \\
           + " train -solver "
           + dir_path + "\\quick_solver.prototxt") # solver path
        


def click_button_1(event):
    cmd = listbox.GetSelection
    if cmd == "createNewDir":
        createDir(startTime())
    elif cmd == "createDataBase":
        createDB()
    elif cmd == "createMean":
        createMean()
    elif cmd == "trainModel":
        trainModel()
    else:
        createDir(startTime())
        createDB()
        createMean()
        trainModel()


def click_openDialog(event):
    result = ""
    # dialog
    dlg = wx.DirDialog(None,"Choose input directory","",
                       wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
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
    trainlist_Panels = getDirPanel(panel, u"trainlist", u"trainlist path", 3)
    testlist_Panels = getDirPanel(panel, u"testlist", u"testlist path", 4)
    caffe_Panels = getDirPanel(panel, u"caffe", u"~/caffe/build/tools", 2)

    # setting resize
    resize_panel = wx.Panel(sub_panel, wx.ID_ANY)
    resize_layout = wx.BoxSizer(wx.VERTICAL)
    resize_Panels = getPrmPanels(
        { u"height":"128", u"width":"128"}, 
        panel, resize_panel, resize_layout)

    # setting prm
    prmdict = {
        u"test_iter":"100",
        u"test_interval":"500",
        u"base_lr":"0.01",
        u"momentum":"0.9",
        u"weight_decay":"0.005",
        u"lr_policy":u"inv",
        u"gamma":"0.0001",
        u"power":"0.75",
        u"display":"100",
        u"max_iter":"10000",
        u"snapshot":"5000",
        u"snapshot_prefix":u"dir_path",
        u"solver_mode":u"GPU"
        }
    prm_panel = wx.Panel(sub_panel, wx.ID_ANY)
    prm_layout = wx.BoxSizer(wx.VERTICAL)
    prm_Panels = getPrmPanels(prmdict, panel, prm_panel, prm_layout)


    # setting execute
    exec_panel = wx.Panel(resize_panel, wx.ID_ANY)
    exec_layout = wx.BoxSizer(wx.HORIZONTAL)
    
    element_array = (
        "createNewDir"
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
    layout.Add(caffe_Panels[0], flag = wx.EXPAND | wx.ALL, border = panel_border)
    sub_layout.Add(prm_panel, flag = wx.EXPAND | wx.ALL, border = panel_border)
    sub_layout.Add(resize_panel, flag = wx.EXPAND | wx.ALL, border = panel_border)

    sub_panel.SetSizer(sub_layout)
    layout.Add(sub_panel, flag = wx.EXPAND | wx.ALL, border = panel_border)
    layout.Add(button_1, flag = wx.EXPAND | wx.ALL, border = panel_border)

    panel.SetSizer(layout)
    frame.Show()
    application.MainLoop()
