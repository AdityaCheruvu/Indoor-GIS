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
    

    