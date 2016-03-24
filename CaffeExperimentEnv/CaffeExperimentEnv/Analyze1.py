#coding:utf-8

import re
import subprocess as s
import glob
import os
import shutil

def getLog():
    logpath = glob.glob("/tmp/caffe.*.*.log.INFO.*.*")
    shutil.copyfile(logpath, "caffe.log")
    os.remove(logpath)

def getInterval():
    loss = readlines("caffe.log", "test_iter:")
    accuracy = readlines("caffe.log", "test_interval:")

    loss = loss[0].replace("test_iter: ", "")
    accuracy = accuracy[0].replace("test_interval:", "")

    return {"loss":int(loss), "accuracy":int(accuracy)}


def readlines(filename, str):
    ld = open(filename, encoding='cp437')
    lines = ld.readlines()
    ld.close()

    result = []
    for line in lines:
        if line.find(str) >= 0:
            result.append(line[:-1])
    return result

def convertLog(strlist, word, interval):
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

    f = open("datatmp.txt","w")
    f.write(result)
    f.close()

def callGnu(word):
    s.call("\"C:\\Program Files\\gnuplot\\bin\\gnuplot\"" + \
             " -persist -e " + \
              "\"" + \
              "set autoscale; " + \
              "set grid; " + \
              "set title '" + word + "'; " + \
              "plot 'datatmp.txt' w l \"" , shell = True)
    
def loadLog(filename, word):
    data = readlines(filename, word)
    interval = getInterval()
    convertLog(data,word,interval[word])
    callGnu(word)

def createLogGraph(sw):
    filename = "caffe.log"
    if sw == 0: # accuracy
        loadLog(filename, "accuracy")
    elif sw == 1: # loss
        loadLog(filename, "loss")
