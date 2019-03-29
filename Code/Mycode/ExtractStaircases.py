from __future__ import division
import ezdxf
import sys
from LineGeometry import *
from GlobalValues import *
from GenCenterLine import *
from GenOutput import *
from itertools import compress
minStairSize = 0
maxStairSize = 3

def getPerpendicularLineEqs(slope, endpoint1, endpoint2):
    if(slope == 0 or slope <= RadianEPS): #can i take it like this?
        slope = Inf 
        constant1 = endpoint1.x
        constant2 = endpoint2.x
    else:
        if(slope == Inf):
            slope = 0
        else:
            slope = -1/slope
        constant1 = endpoint1.y - slope*endpoint1.x
        constant2 = endpoint2.y - slope*endpoint2.x
    return (slope, constant1, constant2)
    
def areEndPointsOnLineEqs(m, c1, c2, endpoint1, endpoint2):
    if(m == Inf):
        if((c1 - endpoint1.x)<=EPS and (c2 - endpoint2.x)<=EPS):
            return True
        else:
            return False
    else:
        if(abs(endpoint1.y - m*endpoint1.x - c1) <= EPS and abs(endpoint2.y - m*endpoint2.x - c2) <= EPS):
            return True
        else:
            return False

def keyToSortLines(line):
    if abs(line.a.x - line.b.x) <= EPS:
        return line.a.x
    elif abs(line.a.y - line.b.y) <= EPS:
        return line.a.y
    return line.a.x
    
def isStairSize(size):
    if(size >= minStairSize and size <= maxStairSize):
        return True
    else:
        return False

def areLineSetsParallel(set1, set2):
    sampleFromSet1 = set1[0]
    sampleFromSet2 = set2[0]
    if(sampleFromSet1.is_parallel(sampleFromSet2)):
        return True
    else:
        return False
 
if __name__ == "__main__":
    arg = sys.argv
    if not (len(arg)==2) :
        print "Usage: python ExtractStaircases.py Filename"
        sys.exit()
    inputFile = arg[1]
    dwg = ezdxf.readfile(inputFile)
    modelspace = dwg.modelspace()

    LineSegmentsFromDwg = [Segment(Point(*line.dxf.start[:-1]), Point(*line.dxf.end[:-1])) for line in modelspace.query('LINE')]
    MakeShapeFile(LineSegmentsFromDwg, "allLines.shp")
    #print(LineSegmentsFromDwg)
    parallelLineSets = {}
    #ask about determination of parallel lines
    for line in LineSegmentsFromDwg:
        try:
            parallelLineSets[line.slope].append(line)
        except:
            parallelLineSets[line.slope] = [line]

    for slope1 in parallelLineSets.keys():
        for slope2 in parallelLineSets.keys():
            if(areLineSetsParallel(list(parallelLineSets[slope1]), list(parallelLineSets[slope1])):
                
    for k in parallelLineSets.keys():
        if len(parallelLineSets[k]) <=1:
            del parallelLineSets[k]
    #for k, v in parallelLineSets.iteritems():
        #print("Slope: " + str(k))
        #for line in v:
            #print(line.coordinates)  
    #print(parallelLineSets) 
    """----------------------------------------------------------------------"""
    parallelLines = []
    for i in parallelLineSets.keys():
        parallelLines+=list(parallelLines)
    MakeShapeFile(parallelLines, "parallelLines.shp")
    print(parallelLineSets.keys())
    """----------------------------------------------------------------------"""
    setsOfProperEndingParallelLines = {}
    for k in parallelLineSets.keys():
        currSet = parallelLineSets[k]
        i = 0
        while(len(currSet)!=0):
            currLine = currSet[i]
            if(i==0):
                m, c1, c2 = getPerpendicularLineEqs(currLine.slope, currLine.a, currLine.b)
                try:
                    setsOfProperEndingParallelLines[(m, c1, c2)].append(currLine)
                except:
                    setsOfProperEndingParallelLines[(m, c1, c2)] = [currLine]
                currSet.remove(currLine)
            else:
                if(areEndPointsOnLineEqs(m, c1, c2, currLine.a, currLine.b)):
                    setsOfProperEndingParallelLines[(m, c1, c2)].append(currLine)
                    currSet.remove(currLine)
                else:
                    i+=1
            if(i >= len(currSet)):
                i=0
    listOfStaircases = []
    #print(setsOfProperEndingParallelLines)
    """----------------------------------------"""
    lines = []
    for i in setsOfProperEndingParallelLines.keys():
        lines+=list(setsOfProperEndingParallelLines[i])
    print(lines, len(lines))
    MakeShapeFile(lines, "trial.shp")
    """-----------------------------------------"""
    
    """for k in setsOfProperEndingParallelLines.keys():
        #print(listOfStaircases)
        #print
        if(len(setsOfProperEndingParallelLines[k]) <= 1):
            del setsOfProperEndingParallelLines[k]
        else:
            setsOfProperEndingParallelLines[k].sort(key=keyToSortLines)
            perpDistances = []
            for i in range(len(setsOfProperEndingParallelLines[k])-1):
                line1 = setsOfProperEndingParallelLines[k][i]
                line2 = setsOfProperEndingParallelLines[k][i+1]
                perpDistances.append(isStairSize(line1.prependiculardistance(line2)))
            tmp = [setsOfProperEndingParallelLines[k][0]]
            for i in range(1, len(setsOfProperEndingParallelLines[k])-1):
                if(perpDistances[i] == True):
                    tmp.append(setsOfProperEndingParallelLines[k][i])
                else:
                    #print(tmp)
                    if(len(tmp) > 2):
                        print("hi")
                        listOfStaircases = listOfStaircases + tmp[:]
                    tmp = []
    #print(listOfStaircases)
    linesOfStairs = []
    #print(setsOfProperEndingParallelLines)
    for l in listOfStaircases:
        linesOfStairs+=l
    #MakeShapeFile(linesOfStairs, "staircases.shp")

        
        
    #print(setsOfProperEndingParallelLines)"""



    


         
    

