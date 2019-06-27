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
minStairSize = 250
maxStairSize = 400
EPSProperParallel = 0.00000001
MinCountOfStairs = 3
#minStepLength = 
#maxStepLength = 
#-----------------------------------------

class setOFSteps():
    def __init__(self, listOfLines):
        self.listOfLines = listOfLines
        self.no_of_steps = len(listOfLines)-1
        self.bounding_rect = (listOfLines[0].a, listOfLines[0].b, listOfLines[-1].a, listOfLines[-1].b)
        line1,line2 = listOfLines[0], listOfLines[-1]
        centroid1 = line1.a.midpoint(line1.b)
        centroid2 = line2.a.midpoint(line2.b)
        self.lineCentroids = (centroid1, centroid2)
        self.centroid = centroid1.midpoint(centroid2)
        self.avgAngleOfRotation = sum([line.angle for line in listOfLines])/len(listOfLines)
        self.stepLength = self.listOfLines[0].length
        self.runningLength = self.lineCentroids[0].distance(self.lineCentroids[1])

    def getNoOfSteps(self):
        return self.no_of_steps
    
    def getListOfLines(self):
        return self.listOfLines
    
    def getBoundingBox(self):
        return self.bounding_rect

    def isConnectedWithSet(self, setA):
        if(not areLineSetsParallel(self.avgAngleOfRotation, setA.avgAngleOfRotation)):
            return False
        
        if(self.listOfLines[0].length < setA.listOfLines[0].length):
            line1 = self.listOfLines[0]
            line2 = setA.listOfLines[0]
        else:
            line2 = self.listOfLines[0]
            line1 = setA.listOfLines[0]
        if(abs(line1.projection(line2).length - line1.length) > EPS):
            return False

        linea1 = self.listOfLines[0]
        lineb1 = setA.listOfLines[0]
        linea2 = self.listOfLines[-1]
        lineb2 = setA.listOfLines[-1]
        if(isStairSize(linea1.prependiculardistance(lineb2))):
            return (True, 'ba') #True, and order of setOfSteps alignment
        elif(isStairSize(lineb1.prependiculardistance(linea2))):
            return (True, 'ab')
        return False
        
    #Before calling this function, make sure you use the same object as u used to call isConnectedWithSet
    def connectSetOfSteps(self, setA, alignment):
        
        self.stepLength = (self.stepLength * self.no_of_steps + setA.stepLength*setA.no_of_steps)/(self.no_of_steps + setA.no_of_steps)
        self.no_of_steps = self.no_of_steps + setA.no_of_steps
        self.avgAngleOfRotation = (self.avgAngleOfRotation * self.no_of_steps + setA.avgAngleOfRotation * setA.no_of_steps)/(self.no_of_steps + setA.no_of_steps)

        if(alignment=="ab"):
            self.listOfLines = self.listOfLines + setA.listOfLines
        elif(alignment=="ba"):
            self.listOfLines = setA.listOfLines + self.listOfLines
        self.bounding_rect = (listOfLines[0].a, listOfLines[0].b, listOfLines[-1].a, listOfLines[-1].b)
        line1,line2 = listOfLines[0], listOfLines[-1]
        centroid1 = line1.a.midpoint(line1.b)
        centroid2 = line2.a.midpoint(line2.b)
        self.lineCentroids = (centroid1, centroid2)
        self.centroid = centroid1.midpoint(centroid2)
        self.runningLength = self.lineCentroids[0].distance(self.lineCentroids[1])

    def mkShapeFileOfSet(self):
        MakeShapeFile(self.listOfLines, "steps.shp")
    
    def __str__(self):
        return str(self.listOfLines)

    """def identifyMidLandings(self, searchSpace):
        l = searchSpace.keys()
        for angle in l:
            if(abs(abs(angle - self.avgAngleOfRotation) - math.pi/2) <= RadianEPS):
                perpendicularAngle = angle
            elif(abs(angle - math.pi/2)):
                parallelAngle = angle
        #els = End Line Segments
        els = (self.listOfLines[0], self.listOfLines[-1])"""
        

class midLanding():
    def __init__(self):
        pass
#-----------------------------------------

#Utility Functions

def getPerpendicularLineEqs(slope, endpoint1, endpoint2):
    """
    Finds a pair of perpendicular lines to the given slope at the given endpoints
    
    slope: slope of the given line
    endpoint1: 1st endpoint of the given line
    endpoint2: 2nd endpoint of the given line

    """
    if(slope == 0 or slope <= RadianEPS): #can i take it like this?
        """
        If slope of given line is 0 or very small, then the target slope
        of perpendicular line is Infinity, and constant is the corresponding x coordinate.
        """
        slope = Inf 
        constant1 = endpoint1.x
        constant2 = endpoint2.x
    else:
        """
        If slope is Infinity, then target slope is 0.
        else it is -1/slope.
        The constant can be calculated using c = y-mx
        """
        if(slope == Inf):
            slope = 0
        else:
            slope = -1/slope
        constant1 = endpoint1.y - slope*endpoint1.x
        constant2 = endpoint2.y - slope*endpoint2.x
    return (slope, constant1, constant2)
    
def areEndPointsOnLineEqs(m, c1, c2, endpoint1, endpoint2):
    """
    Checks if endpoint1 and endpoint2 are on lines y = mx + c1 and y=mx+c2 respectively
    m: slope of given lines.
    c1, c2: constants of each of the line equations.
    endpoint1, endpoint2: points of lines which are being tested.
    """
    if(m == Inf):
        """
        If slope is Infinity, then the equation is satisfied if c-x = 0
        """
        if((c1 - endpoint1.x)<=EPSProperParallel and (c2 - endpoint2.x)<=EPSProperParallel):
            return True
        else:
            return False
    else:
        """
        If slope is any other number, the equation is satisfied if y-mx-c=0
        """
        if(abs(endpoint1.y - m*endpoint1.x - c1) <= EPSProperParallel and abs(endpoint2.y - m*endpoint2.x - c2) <= EPSProperParallel):
            return True
        else:
            return False

def keyToSortLines(line):
    """
    key function to sort list of parallel lines, vertically or horizontally
    based on the orientation of parallel lines.
    """
    if abs(line.a.x - line.b.x) <= EPS:
        return line.a.x
    elif abs(line.a.y - line.b.y) <= EPS:
        return line.a.y
    return line.a.x
    
def isStairSize(size):
    """
    Function to apply threshold on width of a step.
    """
    if(size >= minStairSize and size <= maxStairSize):
        return True
    else:
        return False

def areLineSetsParallel(angle1, angle2):
    """
    Function to determine if 2 line sets can be considered parallel.
    angle1, angle2: degree of rotation in radians of 2 parallel line sets.
    """
    if(angle1 == None or angle2 == None):
        return True
    diff = abs(angle1 - angle2)
    if diff < RadianEPS :
        return True
    if abs(diff - math.pi) < RadianEPS :
        return True
    return False

def findGroupsOfAngles(allAnglesList, allAnglesCount):
    """
    groups different angles of lines found in the drawing, if they can be considered parallel.
    
    allAnglesList: List of all angles of lines without repitition.
    allAnglesCount: Dictionary of all angles mapped to respective count of lines with those angles.
    """
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

def findConnectionBetweenParallelFlightsOfStairs(flight1, flight2):
    if(flight1.bounding_rect[0].distance(flight2.bounding_rect[2]) < flight1.bounding_rect[2].distance(flight2.bounding_rect[0])):
        flight1, flight2 = flight2, flight1

    if(flight1.stepLength < flight2.stepLength):
        line1 = Segment(flight1.bounding_rect[2], Segment(flight2.bounding_rect[0], flight2.bounding_rect[1]).projection(flight1.bounding_rect[2]))
        line2 = Segment(flight1.bounding_rect[3], Segment(flight2.bounding_rect[0], flight2.bounding_rect[1]).projection(flight1.bounding_rect[3]))
    else:
        line1 = Segment(flight2.bounding_rect[0], Segment(flight1.bounding_rect[2], flight1.bounding_rect[3]).projection(flight2.bounding_rect[0]))
        line2 = Segment(flight2.bounding_rect[1], Segment(flight1.bounding_rect[2], flight1.bounding_rect[3]).projection(flight2.bounding_rect[1]))
    
    return (line1, line2)


#-----------------------------------------

if __name__ == "__main__":

    # Recieve file name of the dxf file, read lines from it and make segments
    arg = sys.argv
    if not (len(arg)==2):
        print("Usage: python ExtractStaircases.py Filename")
        sys.exit()
    inputFile = arg[1]
    dwg = ezdxf.readfile(inputFile)
    modelspace = dwg.modelspace()
    LineSegmentsFromDwg = [Segment(Point(*line.dxf.start[:-1]), Point(*line.dxf.end[:-1])) for line in modelspace.query('LINE')]
    """
    i=0
    while(i<len(LineSegmentsFromDwg)):
        if(LineSegmentsFromDwg[i].length > maxStepLength or LineSegmentsFromDwg[i].length < minStepLength):
            del LineSegmentsFromDwg[i]
        else:
            i+=1
    """
    #MakeShapeFile(LineSegmentsFromDwg, "allLines.shp")
    #Develop a Dictionary mapping from angle to count of the number of lines with the angle of rotation
    allAnglesCount = {}
    for line in LineSegmentsFromDwg:
        try:
            allAnglesCount[line.angle]+=1
        except:
            allAnglesCount[line.angle] = 1
    #pprint.pprint(parallelLineSets)
    #print(allAngles)
    #create a sorted list of all angles from the drawing
    allAnglesList = sorted(list(allAnglesCount.keys()))
    #group the angles in order to group almost parallel lines
    groupsOfAngles = findGroupsOfAngles(allAnglesList, allAnglesCount)
    #Develop a dictionary of angles to list of lines from the model space of that angle
    angleToLineMap = {}
    for line in LineSegmentsFromDwg:
        try:
            angleToLineMap[line.angle].append(line)
        except:
            angleToLineMap[line.angle] = [line]
    #Create groups of lines out of the angle groups
    parallelLineSets = {}
    for group in groupsOfAngles:
        parallelLineSets[group[0][0]] = []
        for angle in group[1]:
            parallelLineSets[group[0][0]]+=angleToLineMap[angle]
    
    """
    Code for debugging purpose
    for k, v in parallelLineSets.items():
        print(k, v)
        print(len(v))
    print(len(LineSegmentsFromDwg))"""
    """for k, v in parallelLineSets.iteritems():
        #print("Slope: " + str(k))
        MakeShapeFile(v, str(k)+".shp")"""
    
    #Find set of parallel lines having the similar end points relatively
    setsOfProperEndingParallelLines = {}
    for k in parallelLineSets.keys():
        #for every set of parallel lines, construct a pair of perpendicular line equations
        #from the endpoints of a line in the set and add all lines which have endpoints satisfying
        #the perpendicular line equations into a set.
        currSet = parallelLineSets[k][:]
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
    
    
    #lines = []
    #Remove the sets with lesser lines than MinCountOfStairs
    for k in setsOfProperEndingParallelLines.keys():
        if(len(setsOfProperEndingParallelLines[k]) <= MinCountOfStairs):
            del setsOfProperEndingParallelLines[k]
    """for i in setsOfProperEndingParallelLines.keys():
        lines+=list(setsOfProperEndingParallelLines[i])
    #print(lines, len(lines))
    MakeShapeFile(lines, "trial.shp")"""

    """for k, v in setsOfProperEndingParallelLines.items():
        print("---------------------")
        print(k)
        print
        print(v)

        print(len(v))
    print(len(setsOfProperEndingParallelLines))"""

    #setsOfProperEndingParallelLines = {}
    #Sort each list of lines, find distances between adjacent lines, and split the lists
    #down whenever the distance is out of the threshold.
    listOfStaircases = []
    for k in setsOfProperEndingParallelLines.keys():
        #print(listOfStaircases)
        #print
        if(len(setsOfProperEndingParallelLines[k]) <= 1):
            del setsOfProperEndingParallelLines[k]
        else:
            """for i in setsOfProperEndingParallelLines[k]:
                print(i, (float(i.a.x), float(i.a.y)), (float(i.b.x), float(i.b.y)))"""
            setsOfProperEndingParallelLines[k].sort(key=keyToSortLines)
            """print
            print("-----------------------------------------------")
            print("-----------------------------------------------")
            print
            for i in setsOfProperEndingParallelLines[k]:
                print(i, (float(i.a.x), float(i.a.y)), (float(i.b.x), float(i.b.y)))
            #print(setsOfProperEndingParallelLines[k])"""
            perpDistances = []
            for i in range(len(setsOfProperEndingParallelLines[k])-1):
                line1 = setsOfProperEndingParallelLines[k][i]
                line2 = setsOfProperEndingParallelLines[k][i+1]
                perpDistances.append(isStairSize(line1.prependiculardistance(line2)))
            print(perpDistances)
            tmp = [setsOfProperEndingParallelLines[k][0]]
            for i in range(0, len(setsOfProperEndingParallelLines[k])-1):
                if(perpDistances[i] == True):
                    tmp.append(setsOfProperEndingParallelLines[k][i+1])
                else:
                    #print(tmp)
                    if(len(tmp) > MinCountOfStairs):
                        #print("hi")
                        #print(tmp, len(tmp))
                        listOfStaircases.append(tmp)
                    tmp = [setsOfProperEndingParallelLines[k][i+1]]
            listOfStaircases.append(tmp)
            #print(listOfStaircases, len(listOfStaircases), len(listOfStaircases[0]), len(listOfStaircases[1]))
    #print(listOfStaircases)
    linesOfStairs = []
    #print(setsOfProperEndingParallelLines)
    #for l in listOfStaircases:
    #    pprint.pprint(l)
    #pprint.pprint(listOfStaircases)
    #MakeShapeFile(linesOfStairs, "staircases.shp")

    #listOfStaircases contains all the sets of stairs identified.

    for k in parallelLineSets.keys():
        for i in range(len(listOfStaircases)): 
            parallelLineSets[k] = list(set(parallelLineSets[k])-set(listOfStaircases[i]))
            parallelLineSets[k].sort(key=keyToSortLines)
    print(parallelLineSets.keys())
    for i in range(len(listOfStaircases)):
        listOfStaircases[i] = setOFSteps(listOfStaircases[i])
        
        
        #MakeShapeFile(listOfStaircases[i], "stairsNo"+str(i)+".shp")
    
    #Club all the continuois sets of stairs
    i=0
    j=1
    while(i<len(listOfStaircases)-1):
        j=i+1
        while(j<len(listOfStaircases)):
            isConnected = listOfStaircases[i].isConnectedWithSet(listOfStaircases[j])
            print(isConnected)
            if(isConnected!=False):
                listOfStaircases[i].connectSetOfSteps(listOfStaircases[j], isConnected[1])
                listOfStaircases.pop(j)
            else:
                j+=1
        i+=1            
    """print(listOfStaircases[0].listOfLines, len(listOfStaircases[0].listOfLines))
    print
    print(listOfStaircases[1].listOfLines, len(listOfStaircases[1].listOfLines))"""

    for i in range(len(listOfStaircases)):
        for j in range(i+1, len(listOfStaircases)):
            if(areLineSetsParallel(listOfStaircases[i].avgAngleOfRotation , listOfStaircases[j].avgAngleOfRotation)):
                boundingBox1 = listOfStaircases[i].bounding_rect
                boundingBox2 = listOfStaircases[j].bounding_rect
                line1 = Segment(boundingBox1[0], boundingBox1[1])
                line2 = Segment(boundingBox2[0], boundingBox2[1])
                if(abs(min(line1.length, line2.length) - line1.projection(line2).length) <= EPS):
                    ConnectingLine1, ConnectingLine2 = findConnectionBetweenParallelFlightsOfStairs(listOfStaircases[i], listOfStaircases[j])
                    distance1 = ConnectingLine1.length
                    distance2 = ConnectingLine2.length
                    if(max(distance1, distance2) < min(listOfStaircases[i].runningLength, listOfStaircases[j].runningLength)):
                        print(distance1, distance2, listOfStaircases[i].runningLength, listOfStaircases[j].runningLength)
                        print("Connection Found!")

                    
                    