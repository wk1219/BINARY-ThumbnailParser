#-*- coding:utf-8 -*-
import os
import sys
from internal import common

class ThumbnailParser:
    def __init__(self):
        self.os = None
        self.parser = None



    def SetObject(self, _osv):
        if( self.os != _osv) or (self.os == None):
            self.os = _osv
            if _osv == "win":
                self.parser = ThumbnailParser_WIN()
            elif _osv == "linux":
                self.parser = ThumbnailParser_LNX()
            elif _osv == "mac":
                self.parser = ThumbnailParser_MAC()
            else:
                self.parser = None
        
        if self.parser == None:
            return False
    

            
    def GetData(self, _path):
        if os.path.isfile(_path) == False:
            print("Not file")
            return None
        
        if common.CheckSignature(_path, "thumbnail") == True:
            osv = "win"
        elif common.CheckSignature(_path, "") == True or\
            common.CheckSignature(_path, "") == True:
            osv = "linux"
        else:
            return None
        
        if self.SetObject(osv) == False:
            return None
        
        # if success, dictionary data
        # else, False
        return self.parser.GetData(_path)
    
    def PrintData(self, _dictData):
        self.parser.PrintData(_dictData)
        
'''
Windows
'''
class ThumbnailParser_WIN:
    def GetData(self, _path):        
        
        return dictData.copy()
    
    def PrintData(self, _dictData):
        if type(_dictData) is not dict:
            return False
    


'''
macOS
'''
class ThumbnailParser_MAC:
    def GetData(self, _Path):
        pass


'''
Linux
'''
class ThumbnailParser_LNX:
    def GetData(self, _Path):
        pass



parameters = ["-p", "--path", "-h", "--help", "-o", "--output"]

def PrintWelcome():
    body = \
'''==============================
Thumbnail Parser Version 0.1
==============================\n'''
    print(body)

def PrintHelp():
    body = \
'''how to use this program with parameters
params
    -o, --output
        file path to saving result

    -p, --path
        thumbnail file path(including file)

    -v, --verbose
        save thumbnail image file in running process directory

    -h, --help\n'''
    print(body)

def GetValueOfParam(_paramShort="", _paramLong=""):
    if _paramShort == "" and _paramLong == "":
        return None
    elif (_paramShort in parameters) == False:
        return None
    elif (_paramLong in parameters) == False:
        return None

    val = ""    
    if _paramShort in sys.argv:
        param = _paramShort
    elif _paramLong in sys.argv:
        param = _paramLong
    else:
        return val

    for i in sys.argv:
        if i == param:
            if (sys.argv.index(i) < len(sys.argv)) and (sys.argv.index(i) + 1 < len(sys.argv)):
                val = sys.argv[sys.argv.index(i) + 1]
                break
    return val

if __name__ == "__main__":
    PrintWelcome()
    if len(sys.argv) > 1:
        out = GetValueOfParam("-o", "--output")
        path = GetValueOfParam("-p", "--path")
        
        p = ThumbnailParser()
        if p != None:
            data = p.GetData(path)
            if data != None:
                p.PrintData(data)
                sys.exit(0)
    
    PrintHelp()