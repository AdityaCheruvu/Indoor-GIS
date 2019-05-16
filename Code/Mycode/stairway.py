from __future__ import division
import ezdxf
import sys
from LineGeometry import *
from GlobalValues import *
from GenCenterLine import *
from GenOutput import *
from itertools import compress
import pprint

#-----------------------------------------
#Parameters
minStairSize = 0
maxStairSize = 3
EPSProperParallel = 0.00000001
MinCountOfStairs = 1
#-----------------------------------------

#-----------------------------------------

#Utility Functions

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
        if((c1 - endpoint1.x)<=EPSProperParallel and (c2 - endpoint2.x)<=EPSProperParallel):
            return True
        else:
            return False
    else:
        if(abs(endpoint1.y - m*endpoint1.x - c1) <= EPSProperParallel and abs(endpoint2.y - m*endpoint2.x - c2) <= EPSProperParallel):
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

def areLineSetsParallel(angle1, angle2):
    if(angle1 == None or angle2 == None):
        return True
    diff = abs(angle1 - angle2)
    if diff < RadianEPS :
        return True
    if abs(diff - math.pi) < RadianEPS :
        return True
    return False

def findGroupsOfAngles(allAnglesList, allAngles):
    #Add weighted average still
    i=0
    groupsOfAngles = []
    group = [[None, 0],[]] #[[avg, weight], [angleList]]
    while(len(allAnglesList)!=0):
        if(areLineSetsParallel(group[0][0], allAnglesList[0])):
            if(group[0][0]==None):
                group[0][0] = allAnglesList[0]
                group[0][1] = allAnglesCount[allAnglesList[0]]
                group[1] = [allAnglesList.pop(0)]
            else:
                group[0][0] = (group[0][0]*group[0][1] + allAnglesList[0]*allAnglesCount[allAnglesList[0]])/(group[0][1]+allAnglesCount[allAnglesList[0]])
                group[0][1] = group[0][1]+allAnglesCount[allAnglesList[0]]
                group[1].append(allAnglesList.pop(0))
        else:
            groupsOfAngles.append(group)
            group = [[None, 0],[]]
    if(group[0]!=None):
        groupsOfAngles.append(group)
    #pprint.pprint(groupsOfAngles)
    #print(len(groupsOfAngles))
    return groupsOfAngles

            
#-----------------------------------------

if __name__ == "__main__":
    arg = sys.argv
    if not (len(arg)==2) :
        print "Usage: python ExtractStaircases.py Filename"
        sys.exit()
    inputFile = arg[1]
    dwg = ezdxf.readfile(inputFile)
    modelspace = dwg.modelspace()
    LineSegmentsFromDwg = [Segment(Point(*line.dxf.start[:-1]), Point(*line.dxf.end[:-1])) for line in modelspace.query('LINE')]
    #MakeShapeFile(LineSegmentsFromDwg, "allLines.shp")
    allAnglesCount = {}
    for line in LineSegmentsFromDwg:
        try:
            allAnglesCount[line.angle]+=1
        except:
            allAnglesCount[line.angle] = 1
    #pprint.pprint(parallelLineSets)
    #print(allAngles)
    allAnglesList = sorted(list(allAnglesCount.keys()))
    groupsOfAngles = findGroupsOfAngles(allAnglesList, allAnglesCount)
    angleToLineMap = {}
    for line in LineSegmentsFromDwg:
        try:
            angleToLineMap[line.angle].append(line)
        except:
            angleToLineMap[line.angle] = [line]
    parallelLineSets = {}
    for group in groupsOfAngles:
        parallelLineSets[group[0][0]] = []
        for angle in group[1]:
            parallelLineSets[group[0][0]]+=angleToLineMap[angle]
    
    """for k, v in parallelLineSets.items():
        print(k, v)
        print(len(v))
    print(len(LineSegmentsFromDwg))"""
    """for k, v in parallelLineSets.iteritems():
        #print("Slope: " + str(k))
        MakeShapeFile(v, str(k)+".shp")"""
    
    setsOfProperEndingParallelLines = {}
    for k in parallelLineSets.keys():
        currSet = parallelLineSets[k]
        i = 0
        newLine=True
        while(len(currSet)>0):
            currLine = currSet[i]
            if(newLine): #first, not i
                m, c1, c2 = getPerpendicularLineEqs(currLine.slope, currLine.a, currLine.b)
                try:
                    setsOfProperEndingParallelLines[(m, c1, c2)].append(currLine)
                except:
                    setsOfProperEndingParallelLines[(m, c1, c2)] = [currLine]
                currSet.remove(currLine)
                newLine = False
            else:
                if(areEndPointsOnLineEqs(m, c1, c2, currLine.a, currLine.b)):
                    setsOfProperEndingParallelLines[(m, c1, c2)].append(currLine)
                    currSet.remove(currLine)
                else:
                    i+=1
            if(i >= len(currSet)):
                newLine = True
                i=0
    
    
    lines = []
    
    for k in setsOfProperEndingParallelLines.keys():
        if(len(setsOfProperEndingParallelLines[k]) <= MinCountOfStairs):
            del setsOfProperEndingParallelLines[k]
    for i in setsOfProperEndingParallelLines.keys():
        lines+=list(setsOfProperEndingParallelLines[i])
    #print(lines, len(lines))
    MakeShapeFile(lines, "trial.shp")

    """for k, v in setsOfProperEndingParallelLines.items():
        print("---------------------")
        print(k)
        print
        print(v)

        print(len(v))
    print(len(setsOfProperEndingParallelLines))"""

    #setsOfProperEndingParallelLines = {}
    listOfStaircases = []
    for k in setsOfProperEndingParallelLines.keys():
        #print(listOfStaircases)
        #print
        if(len(setsOfProperEndingParallelLines[k]) <= 1):
            del setsOfProperEndingParallelLines[k]
        else:
            setsOfProperEndingParallelLines[k].sort(key=keyToSortLines)
            print(setsOfProperEndingParallelLines[k])
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
    pprint.pprint(listOfStaircases)
    #MakeShapeFile(linesOfStairs, "staircases.shp")

    