import numpy as np

def getBinary(hex: chr) -> str:
    return bin(int(hex,16))[2:].zfill(4)

def getTag(addr: str, tagSize: int) -> int:
    tagBinary: str = ""
    tag: int = 0
    extra: str
    numHex: int = tagSize // 4
    numExtra: int = tagSize % 4

    for i in range(numHex):
        tagBinary += getBinary(addr[i+2])

    if(numExtra > 0):
        extra = getBinary(addr[i+2])
        for j in range(numExtra):
            tagBinary += extra[j]

    multiplier: int = 1
    for i in range(tagSize-1, -1, -1):
        if(tagBinary[i] == '1'):
            tag += multiplier
        multiplier *= 2
    return tag

def getSet(addr: str, tagsize: int, setsize: int) -> int:
    _set:int = 0
    binaryAddress: str
    setBinary: str

    for i in range(8):
        binaryAddress += getBinary(addr[i+2])
    for i in range(setsize):
        setBinary += binaryAddress[tagsize+i]

    # turn setBinary to decimal
    multiplier:int=1
    for i in range(setsize-1, -1, -1):
        if(setBinary[i]=='1'):
            _set+=multiplier
        multiplier *= 2
    return _set

def checkCache(_set:int,setSizeExp:int, cache,tag:int,counter:int) -> bool:
    if(not setSizeExp): # direct mapped
        if(cache[_set][0]==tag):
            cache[_set][1]=counter
            return True
        else:
            cache[_set][0]=tag
            cache[_set][1]=counter
            return False

    setSize:float = pow(2,setSizeExp)
    j:int = _set*setSize
    emptySpot:int = -1
    smallestCounter:int = -1
    lineToReplace:int = -1
    for i in range(setSize):
        if(cache[i+j][0]==tag):
            cache[i+j][1] = counter
            return True
        elif(cache[i+j][0]==-1):
            emptySpot = i+j
        elif(smallestCounter==-1):
            smallestCounter = cache[i+j][1]
            lineToReplace=i+j
        elif(cache[i+j][1]<smallestCounter):
            smallestCounter = cache[i+j][1]
            lineToReplace=i+j    

    # empty spot?
    if(emptySpot!=-1): # it was empty, now fill it
        cache[emptySpot][0]=tag
        cache[emptySpot][1]=counter
    else:
        cache[lineToReplace][0]=tag
        cache[lineToReplace][1]=counter
    return False

import math as m

def main():
    print("This is a rudimentary cache simulator created in Python 3.11. It is your responsibility to ensure that the parameters you enter make sense")
    print("Cache size is an exponent of 2.  E.g. if the exponent is 3, the cache is 2 to the 3, or 8 bytes")
    print()
    cacheSizeExp:int = int(input("Enter the exponent for the cache size\n"))
    print()
    
    print("Line size is an exponent of 2.  E.g. if the exponent is 3, the cache is 2 to the 3, or 8 bytes")
    lineSizeExp:int = int(input(("Enter the exponent for the line size\n"))) # line size = 2^lineSizeExp, lineSizeExp=size of offset field
    print()

    numLinesExp:int=cacheSizeExp-lineSizeExp
    # numLines = 2^numLinesExp

    setSizeExp:int # zero for direct mapped (2^0 = 1 line / set), numLinesExp for fully associative (1 set)

    fa:str = str(input("Is the cache fully associative? Enter 'Y' or 'y' if yes, any other character if no \n"))

    if(fa.lower() == 'y'):
        setSizeExp=numLinesExp
    else:
        dm:str = str(input("Is the cache direct mapped? Enter 'Y' or 'y' if yes, any other character if no \n"))
        if(dm.lower() == 'y'):
            setSizeExp = 0
        else:
            setSizeExp = int(input("Enter '1' for 2 lines per set, '2' for 4 lines per set, '3' for 8 lines per set, or '4' for 16 lines per set.\n"))
            if(setSizeExp>4 or setSizeExp<1):
                print("Try again. It's your responsibility to enter numbers that make sense\n")
    
    numSetsExp:int = numLinesExp - setSizeExp # set field size
    # zero for fully associative
    tagsize:int = 32 - numSetsExp - lineSizeExp
    numLines:int = int(m.pow(2, numLinesExp))
    cache = np.full((numLines,2),-1, dtype=int)

    for i in range(numLines):
        cache[i,0] = -1 # tag
        cache[i,1] = -1 # access counter
    
    filename:str = str(input("Enter filename \n"))

    counter:int = 0
    hit:bool
    numhits:int = 0

    with open("Trace files/"+filename, "r") as file:
        for line in file:
            elements = line.split(' ')
            
            if len(elements) == 3:
                ls, addr, _bytes = elements
            
            tag:int = getTag(addr, tagsize)
            _set:int

            if(not numSetsExp):
                # if numSetsExp = 0, then number of sets = 1 (2^0=1), and it is fully associative
                # there is only 1 set
                _set = 0
            else:
                _set = getSet(addr, tagsize, numSetsExp)
            # check for hit or miss
            if(checkCache(_set,setSizeExp,cache,tag,counter)):
                numhits += 1
            counter+=1

    hitrate:float = float(numhits) / float(counter)
    print(f"Hits {numhits} accesses {counter} hit rate {hitrate}\n")

    
    numLinesPerSet: int

    





if __name__ == '__main__':
    main()