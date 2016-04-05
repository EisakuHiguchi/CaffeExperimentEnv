#coding:utf-8

import re
import subprocess as s
import glob
import os
import shutil

def getLog(workdir):
    logpath = glob.glob("/tmp/caffe.*.*.log.INFO.*.*")
    print("move Logfile \n" + logpath[0])
    s.call("cp " + logpath[0] + " " + workdir + "/caffe.log",shell=True)
    #shutil.copyfile(logpath[0], workdir + "/")
    os.remove(logpath[0])

def getInterval(filename):
    loss = readlines(filename, "test_iter:")
    accuracy = readlines(filename, "test_interval:")
    loss = loss[0].replace("test_iter: ", "")
    accuracy = accuracy[0].replace("test_interval:", "")
    return {"loss":int(loss), "accuracy":int(accuracy)}


def readlines(filename, str):
    ld = open(filename)
    lines = ld.readlines()
    ld.close()
    result = []
    for line in lines:
        if line.find(str) >= 0:
            result.append(line[:-1])
    return result

def convertLog(dirpath, strlist, word, interval):
    result = ""
    cnt = 0
    for d in strlist:
        if word == "loss":
            data = re.findall('Iteration .*, loss = .*', d)
            for e in data:
                result = result + e.replace('Iteration ', '').replace(',', '').replace('loss = ', '') + '\n'
        else:
            data = re.findall(word + ' = .*', d)
            for e in data:
                result = result + str(interval*cnt) + ' ' + e.replace(word + ' = ', '') + '\n'
        cnt = cnt + 1

    f = open(os.path.join(dirpath, "datatmp.txt"),"w")
    f.write(result)
    f.close()

def callGnu(dirpath, word):
    filename = os.path.join(dirpath, "datatmp.txt")
    s.call("gnuplot -persist -e " + \
        "\"" + \
        "set autoscale; " + \
        "set grid; " + \
        "set title '" + word + "';" + \
        "plot \'" + filename + "\' w l \"", shell = True)
    ## for Win
    #s.call("\"C:\\Program Files\\gnuplot\\bin\\gnuplot\"" + \
    #         " -persist -e " + \
    #          "\"" + \
    #          "set autoscale; " + \
    #          "set grid; " + \
    #          "set title '" + word + "'; " + \
    #          "plot 'datatmp.txt' w l \"" , shell = True)
    
def loadLog(dirpath, word):
    filename = os.path.join(dirpath, "caffe.log")
    data = readlines(filename, word)
    interval = getInterval(filename)
    convertLog(dirpath, data,word,interval[word])
    callGnu(dirpath, word)

def createLogGraph(dirpath, sw):
    if sw == 0: # accuracy
        loadLog(dirpath, "accuracy")
    elif sw == 1: # loss
        loadLog(dirpath, "loss")
