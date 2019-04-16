#-*- coding:utf-8 -*-
import os
import sys
from internal import common
#from internal import IMAGEParser

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
        
        if common.CheckSignature(_path, "thumb") == True:
            osv = "win"
        elif common.CheckSignature(_path, "thumb-linux") == True:
            osv = "linux"
        elif common.CheckSignature(_path, "thumb-mac") == True:
            osv = "mac"
        else:
            return None
        
        if self.SetObject(osv) == False:
            return None
        
        # if success, dictionary data
        # else, False
        return self.parser.GetData(_path)
    


    def PrintData(self, _dictData):
        self.parser.PrintData(_dictData)


    
    def SaveImage(self, _path):
        return self.parser.GetImage(_path)
        
'''
Windows
'''
class ThumbnailParser_WIN:
    def __init__(self):        
        self.db_version = {"WIN_VISTA" : 0x14,
                        "WIN_7" : 0x15,
                        "WIN_8" : 0x1A,
                        "WIN_8v2" : 0x1C,
                        "WIN_8v3" : 0x1E,
                        "WIN_8_1" : 0x1F,
                        "WIN_10" : 0x20}
    
    def GetData(self, _path):                
        file = open(_path, "rb")
      
        # signature : CMMM
        # db_version : 0x15 ~ 0x20
        # type : Windows Vista & 7: 00 = 32, 01 = 96, 02 = 256, 03 = 1024, 04 = sr
        #        Windows 8: 00 = 16, 01 = 32, 02 = 48, 03 = 96, 04 = 256, 05 = 1024, 06 = sr, 07 = wide, 08 = exif
		#        Windows 8.1: 00 = 16, 01 = 32, 02 = 48, 03 = 96, 04 = 256, 05 = 1024, 06 = 1600, 07 = sr, 08 = wide, 09 = exif, 0A = wide_alternate
		#        Windows 10: 00 = 16, 01 = 32, 02 = 48, 03 = 96, 04 = 256, 05 = 768, 06 = 1280, 07 = 1920, 08 = 2560, 09 = sr, 0A = wide, 0B = exif, 0C = wide_alternate, 0D = custom_stream        
        db_header = {"signature" : None,
                    "version" : None,
                    "type" : None}

        cache_entry_info = { # "unknown" : None,        # 8v2, 8v3
                            "firstEntry" : None,        # vista, 7, 8, 8v2, 8v3, 8_1, 10
                            "availableEntry" : None,    # vista, 7, 8, 8v2, 8v3, 8_1, 10
                            "numOfEntries" : None}      # vista, 7, 8, 8v2

        cache_entry = {"signature" : None,      # vista, 7, 8, 8v2, 8v3, 8_1, 10
                    "entrySize" : None,         # vista, 7, 8, 8v2, 8v3, 8_1, 10
                    "entryHash" : None,         # vista, 7, 8, 8v2, 8v3, 8_1, 10
                    "extension" : None,         # vista
                    "nameLength" : None,        # vista, 7, 8, 8v2, 8v3, 8_1, 10
                    "paddingSize" : None,       # vista, 7, 8, 8v2, 8v3, 8_1, 10
                    "dataSize" : None,          # vista, 7, 8, 8v2, 8v3, 8_1, 10
                    "width" : None,             # 8
                    "height" : None,            # 8
                    "dataChecksum" : None,      # vista, 7, 8, 8v2, 8v3, 8_1, 10
                    "headerChecksum" : None}    # vista, 7, 8, 8v2, 8v3, 8_1, 10
        
        # db header check        
        db_header.update({"signature" : common.GetToEndian(file.read(4), 4, False, 's')})
        db_header.update({"version" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})
        db_header.update({"type" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})
        if None in db_header.values():
            return None
        elif db_header.get("signature") != "CMMM":
            return None

        # cache entry info check
        try:
            ver =  db_header.get("version")
            if ver == self.db_version.get("WIN_VISTA") or \
                ver == self.db_version.get("WIN_7") or \
                ver == self.db_version.get("WIN_8"):
                cache_entry_info.update({"firstEntry" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})
                cache_entry_info.update({"availableEntry" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})
                cache_entry_info.update({"numOfEntries" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})

            elif ver == self.db_version.get("WIN_8v2"):
                file.seek(4, 1) # unknown 4 bytes pass
                cache_entry_info.update({"firstEntry" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})
                cache_entry_info.update({"availableEntry" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})
                cache_entry_info.update({"numOfEntries" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})

            elif ver == self.db_version.get("WIN_8v3") or \
                ver == self.db_version.get("WIN_8_1") or \
                ver == self.db_version.get("WIN_10"):
                file.seek(4, 1) # unknown 4 bytes pass
                cache_entry_info.update({"firstEntry" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})
                cache_entry_info.update({"availableEntry" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})

            else:
                return None
        except:
            return None

        if list(cache_entry_info.values()).count(None) >= 2 or \
            cache_entry_info.get("firstEntry") == None:
            return None
        
        # each cache entry extraction
        if ver == self.db_version.get("WIN_8v2"):
            startOffset = 28
        else:
            startOffset = 24

        num = 0
        dictData = {}                
        while True:
            try:
                file.seek(startOffset)                
                cache_entry.clear()

                if ver == self.db_version.get("WIN_VISTA"):
                    cache_entry.update({"signature" : common.GetToEndian(file.read(4), 4, False, 's')})
                    cache_entry.update({"entrySize" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})
                    cache_entry.update({"entryHash" : common.GetToEndian(file.read(8), 8, False, 's')})
                    cache_entry.update({"extension" : common.GetToEndian(file.read(8), 8, False, 'uni')}) # unicode
                    cache_entry.update({"nameLength" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})
                    cache_entry.update({"paddingSize" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})
                    cache_entry.update({"dataSize" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})
                    file.seek(4,1) # unknown 4 bytes pass
                    cache_entry.update({"dataChecksum" : common.GetToEndian(file.read(8), 8, True, 'x')})
                    cache_entry.update({"headerChecksum" : common.GetToEndian(file.read(8), 8, True, 'x')})

                elif ver == self.db_version.get("WIN_7"):
                    cache_entry.update({"signature" : common.GetToEndian(file.read(4), 4, False, 's')})
                    cache_entry.update({"entrySize" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})
                    cache_entry.update({"entryHash" : common.GetToEndian(file.read(8), 8, False, 's')})
                    cache_entry.update({"nameLength" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})
                    cache_entry.update({"paddingSize" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})
                    cache_entry.update({"dataSize" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})
                    file.seek(4,1) # unknown 4 bytes pass
                    cache_entry.update({"dataChecksum" : common.GetToEndian(file.read(8), 8, True, 'x')})
                    cache_entry.update({"headerChecksum" : common.GetToEndian(file.read(8), 8, True, 'x')})

                elif ver == self.db_version.get("WIN_8") or \
                    ver == self.db_version.get("WIN_8v2") or \
                    ver == self.db_version.get("WIN_8v3") or \
                    ver == self.db_version.get("WIN_8_1") or \
                    ver == self.db_version.get("WIN_10"):
                    cache_entry.update({"signature" : common.GetToEndian(file.read(4), 4, False, 's')})
                    cache_entry.update({"entrySize" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})
                    cache_entry.update({"entryHash" : common.GetToEndian(file.read(8), 8, False, 'x')})
                    cache_entry.update({"nameLength" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})
                    cache_entry.update({"paddingSize" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})
                    cache_entry.update({"dataSize" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})
                    cache_entry.update({"width" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})
                    cache_entry.update({"height" : int(common.GetToEndian(file.read(4), 4, True, 'd'), 10)})
                    file.seek(4,1) # unknown 4 bytes pass
                    cache_entry.update({"dataChecksum" : common.GetToEndian(file.read(8), 8, True, 'x')})
                    cache_entry.update({"headerChecksum" : common.GetToEndian(file.read(8), 8, True, 'x')})
                    
                else:
                    break
            except Exception as e:
                break
            
            if cache_entry.get("signature") != "CMMM":
                startOffset = common.FindSignatureInFile(_path, startOffset, 32768, b'CMMM')
                if startOffset != -1:
                    continue
                else:
                    break
            
            # check entry hash
            if int(cache_entry.get("entryHash"), 16) == 0:
                startOffset = file.tell()
                continue
            
            # set offset
            startOffset += cache_entry.get("entrySize")

            # check file info
            try:
                fileName = common.GetToEndian(file.read(cache_entry.get("nameLength")), cache_entry.get("nameLength"), False, 'uni')
                file.seek(cache_entry.get("paddingSize"), 1) # between name ~ data

                if cache_entry.get("dataSize") == 0:
                    continue
                else:
                    data = file.read(cache_entry.get("dataSize"))
                
                # check signature of file
                if common.CheckSignature(data, "bmp") == True:
                    fileName += ".bmp"
                elif common.CheckSignature(data, "jpg") == True:
                    fileName += ".jpg"
                elif common.CheckSignature(data, "png") == True:
                    fileName += ".png"
                elif (ver == self.db_version.get("WIN_VISTA")) and (cache_entry.get("extension") != None):
                    fileName += "." + cache_entry.get("extension")
                    
            except Exception as e:
                break
            
            num += 1
            dictFile = {"fileName" : None,
                        "entryHash" : None,
                        "size" : None,
                        "dimension" : None,
                        "data" : None}

            dictFile.update({"fileName" : fileName})
            dictFile.update({"entryHash" : cache_entry.get("entryHash")})
            dictFile.update({"size" : cache_entry.get("dataSize")})
            dictFile.update({"dimension" : "%sx%s" % (cache_entry.get("width"), cache_entry.get("height"))})
            dictFile.update({"data" : data})
            dictData.update({num : dictFile.copy()})

            self.SaveImage(dictFile.get("fileName"), dictFile.get("data"))
                        
        file.close()

        # {num : {name, data, ...}}
        # - info : thumbnail file info
        # - data : image binary data in thumbnail file
        return dictData.copy()
    


    def PrintData(self, _dictData):
        if type(_dictData) is not dict:
            return False
        
        for i in range(len(_dictData)):
            print("[%s]" % (i+1), end='')
            print("=" * (50 - (len(str(i+1)))))

            print("File Name\t: %s" % _dictData.get(i+1).get("fileName"))
            print("File Size\t: %s" % _dictData.get(i+1).get("size"))
            print("Dimension\t: %s" % _dictData.get(i+1).get("dimension"))
            print("Entry Hash\t: %s" % _dictData.get(i+1).get("entryHash"))
            print("")

    

    # _fileName
    #     thumbnail image file name
    # _data
    #    thumbnail image binary data
    def SaveImage(self, _fileName, _data):
        if type(_data) is not bytes:
            return False

        fileName = _fileName
        # Todo: common 함수로 옮기기
        sep = ["?", "\\", "/", ":", "*", "\"", "<", ">", "|"]
        for i in sep:
            if i in fileName:
                fileName = fileName.replace(i, "_")

        if os.path.isdir(os.path.abspath("export")) == False:
            os.mkdir("export")

        fileName = os.path.abspath("export\\" + fileName)
        
        if os.path.isfile(fileName) == True:
            for i in range(1,100):
                root = os.path.splitext(fileName)[0]
                ext = os.path.splitext(fileName)[1]
                
                temp = root + "_{s}".format(s=i) + ext
                if os.path.isfile(temp) == True:
                    if i >= 99:
                        return False
                    else:
                        continue
                else:
                    fileName = temp
                    break

        elif os.path.isdir(fileName) == True:
            return False
        else:
            pass
        
        try:
            file = open(fileName, "wb")
            file.write(_data)
        except Exception as e:
            pass
        finally:
            file.close()

        

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
        (not supported) file path to saving result

    -p, --path
        thumbnail file path(including file)

    -v, --verbose
        (not supported) save thumbnail image file in running process directory

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
                print("input file(or path) : " + os.path.abspath(path))
                print("")
                p.PrintData(data)
                sys.exit(0)
    
    PrintHelp()