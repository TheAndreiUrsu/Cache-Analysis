'''
    Adapted from cache_sim.cpp from Cheryl Resch.

    cache_sim_controlled.py conducts 7 tests as outlined in the paper, it can be customized to run more or different tests.

    simulatr() is the main program to run the tests.

    Written by Andrei Ursu


    Libraries needed: numpy and matplotlib

    installation:
     * pip install numpy
     * pip install matplotlib
'''

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
    binaryAddress: str = ""
    setBinary: str = ""

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

def checkCache(_set:int,setSizeExp:int, cache,tag:int,counter:int,repl:str) -> bool:
    if(not setSizeExp): # direct mapped
        if(cache[_set][0]==tag):
            cache[_set][1]=counter
            return True
        else: # update entry with lowest counter
            cache[_set][0]=tag
            cache[_set][1]=counter
            return False

    setSize:float = pow(2,setSizeExp)
    j:int = _set*setSize
    emptySpot:int = -1
    smallestCounter:int = -1
    lineToReplace:int = -1
    for i in range(setSize):
        if(repl == "FIFO" and cache[i+j][0]==tag):
            return True
        elif(repl == "LRU" and cache[i+j][0]==tag):
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

colors = {
    "Direct Mapped": 'c',
    "Fully Associative (FIFO)": 'r',
    "Fully Associative (LRU)": 'darkred',
    "2-Way Set Associative (FIFO)": 'g',
    "2-Way Set Associative (LRU)": 'darkgreen',
    "4-Way Set Associative (FIFO)": 'b',
    "4-Way Set Associative (LRU)": 'darkblue'
}

def simulatr(associtativity:str,replacement:str="",lines:int=0,cacheSize:int=14,lineSize:int=6):
    cnt = 0
    if(replacement):
        current_assoc = associtativity+ " ("+replacement+")"
    else:
        current_assoc = associtativity
    
    x=[] # stores cache size
    y=[] # stores hit rate

    filename = "gcc.trace"
    print(f"Currently using a {current_assoc} associativity.")
    
    lineSizeExp:int = lineSize # line size = 2^lineSizeExp, lineSizeExp=size of offset field
    print(f"Line size is an exponent of 2. Currently it is {int(m.pow(2,lineSizeExp))} bytes.")
    print()

    cacheSizeExp:int = cacheSize

    linesPerSet:int = int(lines)

    # runs the 5 different cache sizes
    while cnt < 5:
        x.append(int(m.pow(2,cacheSizeExp)))
        print(f"Cache size is an exponent of 2. Currently it is {int(m.pow(2,cacheSizeExp))} bytes.")
        print()

        numLinesExp:int=cacheSizeExp-lineSizeExp
        # numLines = 2^numLinesExp

        setSizeExp:int=0 # zero for direct mapped (2^0 = 1 line / set), numLinesExp for fully associative (1 set)
        
        if("Fully Associative" in current_assoc):
            setSizeExp = numLinesExp
        else:
            if(current_assoc == "Direct Mapped"):
                setSizeExp = 0
            else:
                setSizeExp = linesPerSet # 1 = 2 lines/set, 2 = 4 lines/set, 3 = 8 lines/set, 4 = 16 lines/set

        numSetsExp:int = numLinesExp - setSizeExp # set field size
        # zero for fully associative
        tagsize:int = 32 - numSetsExp - lineSizeExp
        numLines:int = int(m.pow(2, numLinesExp))
        cache = np.full((numLines,2),-1, dtype=int)

        for i in range(numLines):
            cache[i,0] = -1 # tag
            cache[i,1] = -1 # access counter

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
                if(checkCache(_set,setSizeExp,cache,tag,counter,replacement)):
                    numhits += 1
                counter+=1

        hitrate:float = float(numhits) / float(counter)
        print(f"Hits {numhits} accesses {counter} hit rate {hitrate}\n")

        y.append(hitrate)

        cacheSizeExp -= 1

        cnt+=1

    # used for the csv
    _dict = {x[i] : y[i] for i in range(len(y))}

  #  print(_dict)

    # write to csv the data values
    with open("data/"+current_assoc+".csv", 'w', newline='') as file:
        csvwriter = csv.DictWriter(file,fieldnames=['Cache Size','Hit Rate'])
        csvwriter.writeheader()

        for key, val in _dict.items():
            csvwriter.writerow({'Cache Size' : key, 'Hit Rate' : f'{val:.2%}'})

    plt.plot(x,y,marker='o',color=colors.get(current_assoc),label=current_assoc)


if __name__ == '__main__':
    import math as m
    import matplotlib.pyplot as plt
    import csv
    import numpy as np

    print("This is a rudimentary cache simulator created in Python 3.11.\nThe parameters have been chosen and will be displayed in a line plot following the program execution.")
    print(f"We will be using gcc.trace for this simulation.\n")
    print("====== Begin Direct Mapped ======")
    simulatr("Direct Mapped")
    print("====== Begin Fully Associative FIFO ======")
    simulatr("Fully Associative", "FIFO")
    print("====== Begin Fully Associative LRU ======")
    simulatr("Fully Associative", "LRU")
    print("====== Begin 2-Way Set Associative FIFO ======")
    simulatr("2-Way Set Associative", "FIFO",lines=1)
    print("====== Begin 2-Way Set Associative LRU ======")
    simulatr("2-Way Set Associative", "LRU",lines=1)
    print("====== Begin 4-Way Set Associative FIFO ======")
    simulatr("4-Way Set Associative", "FIFO",lines=2)
    print("====== Begin 4-Way Set Associative LRU ======")
    simulatr("4-Way Set Associative", "LRU",lines=2)

    plt.xlabel("Cache Size (bytes)")
    plt.ylabel("Hit Rate")
    plt.title("Hit Rate vs. Cache Size for Different Cache Designs")
    plt.grid()
    plt.xlim(0,18000)
    plt.ylim(0.75,1.05)
    plt.legend()
    plt.show()
