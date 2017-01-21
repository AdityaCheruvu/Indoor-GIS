from osgeo import ogr
import os
import sys


    

# Get the input Layer
def main_code():
    argument = sys.argv
        if not (len(argument)==2) :
            print "Usage: python ExtractLine.py Filename"
            inShapefile = "1roomr.shp"
            # file to use if user doesnot provide input file
        else:
        inShapefile = argument[1]
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(inShapefile, 0)
    inLayer = inDataSource.GetLayer()

    # Create the output Layer
    outShapefile1 = "door.shp"
    outShapefile2 = "door-point.shp"
    outDriver = ogr.GetDriverByName("ESRI Shapefile")

    # Remove output shapefile if it already exists
    if os.path.exists(outShapefile1):
        outDriver.DeleteDataSource(outShapefile1)
    if os.path.exists(outShapefile2):
        outDriver.DeleteDataSource(outShapefile2)
    # Create the output shapefile
    outDataSource = outDriver.CreateDataSource(outShapefile1)
    outDataSource2 = outDriver.CreateDataSource(outShapefile1)
    outLayer = outDataSource.CreateLayer("door", geom_type=ogr.wkbLineString)
    outLayer2 = outDataSource.CreateLayer("doorp", geom_type=ogr.wkbPoint)

    # Add input Layer Fields to the output Layer
    inLayerDefn = inLayer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)
        outLayer2.CreateField(fieldDefn)
    idField = ogr.FieldDefn("Type", ogr.OFTString)
    outLayer2.CreateField(idField)
    idField = ogr.FieldDefn("Openings", ogr.OFTString)
    outLayer2.CreateField(idField)
    idField = ogr.FieldDefn("Capacity", ogr.OFTInteger)
    outLayer2.CreateField(idField)
    idField = ogr.FieldDefn("Cost", ogr.OFTReal)
    outLayer2.CreateField(idField)
    # Get the output Layer's Feature Definition
    outLayerDefn = outLayer.GetLayerDefn()
    outFeature = ogr.Feature(outLayerDefn)
    outLayerDefn2 = outLayer2.GetLayerDefn()
    outFeature2 = ogr.Feature(outLayerDefn2)
    print inLayer.GetFeatureCount()
    geom=[]
    # Add features to the ouput Layer
    no= inLayer.GetFeatureCount()
    for i in range(0, no):
        # Get the input Feature
        inFeature = inLayer.GetFeature(i)
        # Create output Feature
        # Add field values from input Layer
        geo=inFeature.GetGeometryRef()
        points=geo.GetPoints()

        geom.append(points[0])
        geom.append(points[1])
        outFeature.SetGeometry(geo)
        outLayer.CreateFeature(outFeature)

    for i in range(0, 2*no):
        for j in range(i+1, 2*no):
            if geom[i]==geom[j]:
                print "same"
            elif distance_between(geom[i],geom[j])<=0.001:
                print "probably same"
            elif distance_between(geom[i],geom[j])<=0.1:
                print "door"
                print geom[i]
                print geom[j]
                pg1 = ogr.Geometry(ogr.wkbPoint)
                pg2 = ogr.Geometry(ogr.wkbPoint)
                line = ogr.Geometry(ogr.wkbLineString)
                line.AddPoint(geom[i][0], geom[i][1])
                line.AddPoint(geom[j][0], geom[j][1])
                center=line.Centroid()

              #  pg1.AddPoint(geom[i][0], geom[i][1])
               # pg2.AddPoint(geom[j][0], geom[j][1])
               # outFeature.SetGeometry(pg1)

               # outLayer.CreateFeature(outFeature)
               # outFeature.SetGeometry(pg2)
               # outLayer.CreateFeature(outFeature)
                outFeature.SetGeometry(line)
                outLayer.CreateFeature(outFeature)
                outFeature2.SetGeometry(center)
                outLayer2.CreateFeature(outFeature2)
                outFeature2.SetField("Type", "door")
                outFeature2.SetField("Openings","Door-opening")
                outFeature2.SetField("Capacity", 30)
                outFeature2.SetField("Cost", 34.5)
            else:
                print "nothing"


            # Close DataSources

    inDataSource.Destroy()
    outDataSource.Destroy()
    outDataSource2.Destroy()
def distance_between(pt1, pt2):
    """
    :param pt1: First Point
    :param pt2: Second Point
    :return: Distance between points
    """
    pg1 = ogr.Geometry(ogr.wkbPoint)
    pg2 = ogr.Geometry(ogr.wkbPoint)

    pg1.AddPoint(pt1[0], pt1[1])
    pg2.AddPoint(pt2[0], pt2[1])

    return pg1.Distance(pg2)


if __name__ == '__main__':
    main_code()

# Add new feature to output Layer
#outLayer.CreateFeature(outFeature)
