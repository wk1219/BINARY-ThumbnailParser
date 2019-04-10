# -*- coding: utf-8 -*-
import subprocess
import platform
import os
import chardet

# _strNumber : b, o, d, x, s(str)
def GetToEndian(_bytesArr, _bytesCount, _isLittleEndian, _strNumber='x'):
    if _bytesArr == b'' or _bytesCount == 0:
        return ""

    bytesArr = _bytesArr

    if _strNumber == "uni":
        bytesArr = _bytesArr.decode('utf-16', errors='ignore')
    elif _strNumber == "s":
        bytesArr = _bytesArr.decode(chardet.detect(_bytesArr)['encoding'])

    listData= list(bytesArr)
    listData = listData[0:len(listData)]

    if _isLittleEndian == True:
        listData.reverse()

    tupleData= tuple(listData)
    if _strNumber == "b":
        Number = '%08b'
    elif _strNumber == "o":
        Number = '%03o'
    elif _strNumber == "x" or _strNumber == "d":
        Number = '%02X'
    elif _strNumber == "s" or _strNumber == "uni":
        Number = '%c'

    fmt = Number * len(listData)
    string = fmt % tupleData
    if _strNumber == "d":
        if len(listData) > 0:
            string = str(int(string, 16))

    return string

def CheckFlag(_data, _value):
    return (_data & _value ) == _value

def CheckBitFlag(_data, _value):
    p = pow(2, _value) 
    return (_data & p) == p

def CheckPlatform():
    os = platform.system()
    if os == "Darwin":
        os = "Mac"
    print(os)
    return os

def CheckSignature(_path, _extension):
    if (type(_path) == str) and (os.path.isfile(_path) == True):
        size = os.path.getsize(_path)
        file = open(_path, "rb")
        if size > 40:
            file.seek(0)
            fileHeader = file.read(20)

            file.seek(-20, 2)
            fileFooter = file.read(20)
        elif 10 < size <= 40:
            file.seek(0)
            fileHeader = file.read(5)

            file.seek(-5, 2)
            fileFooter = file.read(5)
        elif 4 < size <= 10:
            file.seek(0)
            fileHeader = file.read(4)

            file.seek(-4, 2)
            fileFooter = file.read(4)
        else:
            fileHeader = None

        file.close()
    elif (type(_path) == bytes) or (type(_path) == bytearray):
        size = len(_path)
        if size > 40:
            fileHeader = _path[:20]
            fileFooter = _path[-20:]
        elif 10 < size <= 40:
            fileHeader = _path[:5]
            fileFooter = _path[-5:]
        elif 4 < size <= 10:
            fileHeader = _path[:4]
            fileFooter = _path[-4:]
        else:
            fileHeader = None
    else:
        return False
    
    if fileHeader == None:
        return False

    list = [
        {"ext" : "lnk",
        "header" : [b"\x4C\x00\x00\x00"],
        "footer" : None},
        {"ext" : "exe",
        "header" : [b"\x4D\x5A"],
        "footer" : None},
        {"ext" : "thumb",
        "header" : [b"\x43\x4D\x4D\x4D"],
        "footer" : None},
        {"ext" : "thumb", # thumb-subheader
        "header" : [b"\xFD\xFF\xFF\xFF", None, None, None, None, None, None, None, None,\
            b"\x04\x00\x00\x00"],
        "footer" : None},
        {"ext" : "jpg",
        "header" : [b"\xFF\xD8\xFF\xE0", None, None, b"\x4A\x46\x49\x46"],
        "footer" : None},
        {"ext" : "jpg",
        "header" : [b"\xFF\xD8\xFF\xE1", None, None, b"\x45\x78\x69\x66"],
        "footer" : None},
        {"ext" : "jpg",
        "header" : [b"\xFF\xD8\xFF\xE8", None, None, b"\x53\x50\x49\x46\x46\x00"],
        "footer" : None},
        {"ext" : "png",
        "header" : [b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"],
        "footer" : None},
        {"ext" : "bmp",
        "header" : [b"\x42\x4D"],
        "footer" : None}
    ]

    bFind = False
    for e in list:
        if e["ext"] == _extension.lower():
            # check header
            bFind = False
            fileHeaderIdx = 0
            for h in e["header"]:
                if h == None:
                    fileHeaderIdx += 1
                    continue

                if fileHeaderIdx + len(h) < len(fileHeader):
                    idx = fileHeader[fileHeaderIdx:fileHeaderIdx + len(h)].find(h)
                    if idx != 0:
                        break
                    else:
                        fileHeaderIdx = fileHeaderIdx + idx + len(h)
                        if e["header"].index(h) == (len(e["header"]) -1 ):
                            bFind = True
                        continue
                else:
                    break
            
            if bFind == False:
                continue
            
            # check footer
            bFind = False
            fileHeaderIdx = 0
            if e["footer"] == None:
                bFind = True
            else:
                for f in e["footer"]:
                    if f == None:
                        fileHeaderIdx += 1
                        continue
                    
                    if fileHeaderIdx + len(f) < len(fileHeader):
                        idx = fileHeader[fileHeaderIdx:fileHeaderIdx + len(f)].find(f)
                        if idx != 0:
                            break
                        else:
                            fileHeaderIdx = fileHeaderIdx + idx + len(f)
                            if e["footer"].index(f) == len(f):
                                bFind = True
                            continue
                    else:
                        break
                    
            if bFind == True:
                break

    return bFind

'''
windows 64bit filetime to localtime
'''
def ConvertFiletimeToDatetime(ft):
    import datetime

    EPOCH_AS_FILETIME = 116444736000000000  # 1970-01-01 as MS file time
    HUNDREDS_OF_NANOSECONDS = 10000000

    return datetime.datetime.utcfromtimestamp((ft - EPOCH_AS_FILETIME) / HUNDREDS_OF_NANOSECONDS)



'''
_path
    file path

_startOffset
    offset

_sizeOfChunk
    chunk size

_signature
    bytes

return
    offset of signature in file.
'''
def FindSignatureInFile(_path, _startOffset = 0, _sizeOfChunk = 32768, _signature = b''):
    if os.path.isfile(_path) == False:
        return -1
    
    size = size = os.path.getsize(_path)
    if size < _startOffset:
        return -1
    else:
        startOffset = _startOffset
    
    if size < _sizeOfChunk:
        return -1
    elif _sizeOfChunk == 0:
        chunkSize = 32768
    else:
        chunkSize = _sizeOfChunk

    if _signature == b'':
        return -1
    else:
        sig = _signature

    file = open(_path, "rb")
    currentOffset = startOffset
    while True:
        file.seek(currentOffset)
        buf = file.read(chunkSize)

        currentOffset = 0
        size = len(buf)
        if size <= 4:
            currentOffset = -1
            break
    
        while True:
            if( size > 4 ) and buf[currentOffset:currentOffset+len(sig)] != sig:
                size -= 1
                currentOffset += 1
            else:
                break
        
        if size < 4:
            continue
        else:
            currentOffset += startOffset
            break
    
    file.close()
    return currentOffset