#coding:utf-8

import re
import subprocess as s


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
    convertLog(data,word,500)
    callGnu(word)
