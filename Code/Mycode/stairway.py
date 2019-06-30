from __future__ import division
import ezdxf
import sys
from LineGeometry import *
from GlobalValues import *
from GenCenterLine import *
from GenOutput import *
from itertools import compress
import pprint
import math

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
    def __init__(self, listOfLines):
        self.listOfLines = listOfLines
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

def areLineSetsPerpendicular(angle1, angle2):
    """
    Function to determine if 2 line sets can be considered perpendicular.
    angle1, angle2: degree of rotation in radians of 2 line sets.
    """
    diff = abs(angle1 - angle2)
    if abs(diff - math.pi/2) < RadianEPS :
        return True
    if abs(abs(diff - math.pi)-math.pi/2) < RadianEPS :
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
    
    boundingLine1 = Segment(flight1.bounding_rect[2], flight1.bounding_rect[3])
    boundingLine2 = Segment(flight2.bounding_rect[0], flight2.bounding_rect[1])
    return (line1, line2, boundingLine1, boundingLine2)

def searchLinesInSearchSpace(linesToSearch, searchSpace):
    """
    linesToSearch: list of lines assumed virtually, to be searched in the searchSpace
    searchSpace: list of lines extracted from drawing to search in

    Returns a list of lines with all lines found in the search, and those which are not found in the search.
    """
    listToReturn = []
    for L in searchSpace:
        i=0
        while(i<len(linesToSearch)):
            if(linesToSearch[i].a == L.a and linesToSearch[i].b == L.b):
                listToReturn.append(linesToSearch[i])
                linesToSearch.pop(i)
            i+=1
    listToReturn+=linesToSearch
    return listToReturn

def areaOfTriangle(a, b, c):
    return (abs(a.x*(b.y-c.y) + b.x*(c.y-a.y) + c.x*(a.y-b.y)))/2

def closeMidlanding(referenceLine, referencePoint, d):
    perpEqs = getPerpendicularLineEqs(referenceLine.slope, referenceLine.a, referenceLine.b)
    referenceLineEq = (referenceLine.slope, referenceLine.a.y - referenceLine.slope*referenceLine.a.x)
    substitutedReferenceValue = referencePoint.y - referenceLineEq[0]*referencePoint.x - referenceLineEq[1]

    a, b = referenceLine.a, referenceLine.b
    theta = referenceLine.angle
    perpendicularPointPair1 = (Point(a.x + d*sin(theta), a.y - d*cos(theta)), Point(b.x + d*sin(theta), b.y - d*cos(theta)))
    perpendicularPointPair2 = (Point(a.x - d*sin(theta), a.y + d*cos(theta)), Point(b.x - d*sin(theta), b.y + d*cos(theta)))
    substitutedValue1 = perpendicularPointPair1[0].y - referenceLineEq[0]*perpendicularPointPair1[0].x - referenceLineEq[1]
    substitutedValue2 = perpendicularPointPair2[0].y - referenceLineEq[0]*perpendicularPointPair2[0].x - referenceLineEq[1]
    if(substitutedReferenceValue*substitutedValue1 < 0):
        pair = perpendicularPointPair1
    else:
        pair = perpendicularPointPair2
    
    perpendicularSegments = [Segment(pair[0], referenceLine.a), Segment(pair[1], referenceLine.b), Segment(pair[0], pair[1])]
    return perpendicularSegments

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
    print("List of original lines has size, ", len(LineSegmentsFromDwg))

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

    LineSegmentsFromDwg = set(LineSegmentsFromDwg)
    for i in listOfStaircases:
        LineSegmentsFromDwg = LineSegmentsFromDwg - set(i)
    RemainingSearchSpace = list(LineSegmentsFromDwg)

    print("List of lines has size: ", len(LineSegmentsFromDwg))
    print("List of Remaining search space has size: ", len(RemainingSearchSpace))

    for i in range(len(listOfStaircases)):
        listOfStaircases[i] = setOFSteps(listOfStaircases[i])
    

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

    pairs = []
    midLandings = []
    for i in range(len(listOfStaircases)):
        for j in range(i+1, len(listOfStaircases)):
            midLand = []
            if(areLineSetsParallel(listOfStaircases[i].avgAngleOfRotation , listOfStaircases[j].avgAngleOfRotation)):
                boundingBox1 = listOfStaircases[i].bounding_rect
                boundingBox2 = listOfStaircases[j].bounding_rect
                line1 = Segment(boundingBox1[0], boundingBox1[1])
                line2 = Segment(boundingBox2[0], boundingBox2[1])
                midLandingWidth = min(listOfStaircases[i].stepLength, listOfStaircases[j].stepLength)
                maxMidLandingLength = min(listOfStaircases[i].runningLength, listOfStaircases[j].runningLength)
                if(abs(min(line1.length, line2.length) - line1.projection(line2).length) <= EPS):
                    ConnectingLine1, ConnectingLine2, boundingLine1, boundingLine2 = findConnectionBetweenParallelFlightsOfStairs(listOfStaircases[i], listOfStaircases[j])
                    distance1 = ConnectingLine1.length
                    distance2 = ConnectingLine2.length
                    if(max(distance1, distance2) < min(listOfStaircases[i].runningLength, listOfStaircases[j].runningLength)):
                        print(distance1, distance2, listOfStaircases[i].runningLength, listOfStaircases[j].runningLength)
                        print("Connection Found!")

                        midLand = [ConnectingLine1, ConnectingLine2, boundingLine1, boundingLine2]
                        midLand = searchLinesInSearchSpace(midLand, RemainingSearchSpace)
                        #Do something with the midlanding
                else:

                    #distanceBetweenFlights1 = min(boundingBox1[1].distance(boundingBox2[0]), boundingBox1[0].distance(boundingBox2[1]))
                    #distanceBetweenFlights2 = min(boundingBox1[2].distance(boundingBox2[3]), boundingBox1[3].distance(boundingBox2[2]))
                    leftDistance = boundingBox1[0].distance(Segment(boundingBox2[1], boundingBox2[3]).projection(boundingBox1[0]))
                    rightDistance = boundingBox1[1].distance(Segment(boundingBox2[0], boundingBox2[2]).projection(boundingBox1[1]))
                    upperDifference = boundingBox1[0].distance(Segment(boundingBox1[0], boundingBox1[2]).projection(boundingBox2[0]))
                    lowerDifference = boundingBox1[3].distance(Segment(boundingBox1[0], boundingBox1[2]).projection(boundingBox2[3]))
                    if(abs(listOfStaircases[i].runningLength - listOfStaircases[j].runningLenth) < maxStairSize and min(leftDistance, rightDistance)<maxStairSize and min(upperDifference, lowerDifference)<maxStairSize):
                        #--------------------------------------------------------------
                        configuration = ""
                        if(leftDistance < rightDistance):
                            configuration+="l"
                        else:
                            configuration+="r"
                        if(upperDifference<lowerDifference):
                            configuration+="u"
                        else:
                            configuration+="d"
                        #--------------------------------------------------------------
                        if(configuration=="lu"):
                            boundingLine1 = Segment(boundingBox2[0], boundingBox1[1])
                            connectingLine1, connectingLine2, boundingLine2 = closeMidlanding(boundingLine1, boundingBox1[3], midLandingWidth)
                        elif(configuration=="ld"):
                            boundingLine1 = Segment(boundingBox2[2], boundingBox1[3])
                            connectingLine1, connectingLine2, boundingLine2 = closeMidlanding(boundingLine1, boundingBox1[0], midLandingWidth)
                        elif(configuration=="ru"):
                            boundingLine1 = Segment(boundingBox1[0], boundingBox2[1])
                            connectingLine1, connectingLine2, boundingLine2 = closeMidlanding(boundingLine1, boundingBox1[3], midLandingWidth)
                        else:
                            boundingLine1 = Segment(boundingBox1[2], boundingBox2[3])
                            connectingLine1, connectingLine2, boundingLine2 = closeMidlanding(boundingLine1, boundingBox1[0], midLandingWidth)
                        midLand = [ConnectingLine1, ConnectingLine2, boundingLine1, boundingLine2]
                        midLand = searchLinesInSearchSpace(midLand, RemainingSearchSpace)
                    else:
                        distanceBetweenCentroids1 = listOfStaircases[i].lineCentroids[0].distance(listOfStaircases[j].lineCentroids[1])
                        distanceBetweenCentroids2 = listOfStaircases[i].lineCentroids[1].distance(listOfStaircases[j].lineCentroids[0])
                        if(distanceBetweenCentroids1 > distanceBetweenCentroids2):
                            seg1 = Segment(boundingBox1[2], boundingBox1[3])
                            seg2 = Segment(boundingBox2[0], boundingBox2[1])

                        else:
                            seg1 = Segment(boundingBox1[0], boundingBox1[1])
                            seg2 = Segment(boundingBox2[2], boundingBox2[3])

                        if(seg1.a.distance(seg2.b) < seg1.b.distance(seg2.a)):
                            connectingLine1 = Segment(seg1.b, seg2.projection(seg1.b))
                            connectingLine2 = Segment(seg2.a, seg1.projection(seg2.a))
                                
                        else:
                            connectingLine1 = Segment(seg2.b, seg1.projection(seg2.b))
                            connectingLine2 = Segment(seg1.a, seg2.projection(seg1.a))
                        boundingLine1 = Segment(connectingLine1.a, connectingLine2.a)
                        boundingLine2 = Segment(connectingLine1.b, connectingLine2.b)
                        if(max(connectingLine1.length, boundingLine1.length) < maxMidLandingLength):
                            midLand = [connectingLine1, connectingLine2, boundingLine1, boundingLine2]
                            midLand = searchLinesInSearchSpace(midLand, RemainingSearchSpace)

            elif(areLineSetsPerpendicular(listOfStaircases[i].avgAngleOfRotation, listOfStaircases[j].avgAngleOfRotation)):
                commonCorner = []
                for i in range(len(boundingBox1)):
                    for j in range(len(boundingBox2)):
                        if(boundingBox1[i].distance(boundingBox2[j]) < maxStairSize):
                            commonCorner = [i, j]
                            break
                if(len(commonCorner)!=0):
                    linesOfCommonCorner = []
                    if i==0 or i==1:
                        linesOfCommonCorner.append(Segment(boundingBox1[0]), Segment(boundingBox1[1]))
                    else:
                        linesOfCommonCorner.append(Segment(boundingBox1[2]), Segment(boundingBox1[3]))
                    if j==0 or j==1:
                        linesOfCommonCorner.append(Segment(boundingBox2[0]), Segment(boundingBox2[1]))
                    else:
                        linesOfCommonCorner.append(Segment(boundingBox2[2]), Segment(boundingBox2[3]))

                    cornerPoint = linesOfCommonCorner[0].extendedintersection(linesOfCommonCorner[1])
                    linesOfCommonCorner[0] = ExtendLineSegment(linesOfCommonCorner[0], cornerPoint)
                    linesOfCommonCorner[1] = ExtendLineSegment(linesOfCommonCorner[1], cornerPoint)

                    if(max([line.length for line in linesOfCommonCorner]) < maxMidLandingLength):
                        refLine = linesOfCommonCorner[0]
                        l1, l2, l3 = closeMidlanding(refLine, boundingBox1[(i+2)%4], linesOfCommonCorner[1].length)
                        midLand = [refLine, l1, l2, l3]
                        midLand = searchLinesInSearchSpace(midLand, RemainingSearchSpace)

            else:
                commonCorner = []
                for i in range(len(boundingBox1)):
                    for j in range(len(boundingBox2)):
                        if(boundingBox1[i].distance(boundingBox2[j]) < maxStairSize):
                            commonCorner = [i, j]
                            break
                if(len(commonCorner)!=0):
                    linesOfCommonCorner = []
                    if i==0 or i==1:
                        linesOfCommonCorner.append(Segment(boundingBox1[0]), Segment(boundingBox1[1]))
                    else:
                        linesOfCommonCorner.append(Segment(boundingBox1[2]), Segment(boundingBox1[3]))
                    if j==0 or j==1:
                        linesOfCommonCorner.append(Segment(boundingBox2[0]), Segment(boundingBox2[1]))
                    else:
                        linesOfCommonCorner.append(Segment(boundingBox2[2]), Segment(boundingBox2[3]))

                    connectingLinePair1 = [Segment(linesOfCommonCorner[0].a, linesOfCommonCorner[1].a), Segment(linesOfCommonCorner[0].b, linesOfCommonCorner[1].b)]
                    connectingLinePair2 = [Segment(linesOfCommonCorner[0].a, linesOfCommonCorner[1].b), Segment(linesOfCommonCorner[0].b, linesOfCommonCorner[1].a)]

                    if(max([line.length for line in connectingLinePair1]) < max([line.length for line in connectingLinePair2])):
                        connectingLinePair = connectingLinePair1
                    else:
                        connectingLinePair = connectingLinePair2

                    if(max([line.length for line in connectingLinePair]) < maxMidLandingLength):
                        midLand = connectingLinePair + linesOfCommonCorner
                        midLand = searchLinesInSearchSpace(midLand, RemainingSearchSpace)
                    
            if(len(midLand)!=0):
                pairs.append(set([midLanding(midLand), listOfStaircases[i], listOfStaircases[j]]))

    print(pairs)

    listToPrint = []
    for i in pairs[0]:
        listToPrint+=i.listOfLines
    MakeShapeFile(listToPrint, "Staircase.shp")
    if(len(pairs) > 1):
        i = 0
        j = 1
        while(i<len(pairs)-1):
            j = i+1
            while(j<len(pairs)):
                if(len(pairs[i] &  pairs[j]) != 0):
                    temp = pairs.pop(j)
                    pairs[i] = pairs[i].union(pairs[j])
                else:
                    j+=1
            i+=1

    print(pairs)

            
