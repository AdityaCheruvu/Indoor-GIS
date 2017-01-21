from osgeo import ogr
import os
import sys

def main():
    argument = sys.argv
    if not (len(argument)==2) :
        print "Usage: python ExtractLine.py Filename"
        inShapefile = "door.shp"
        # file to use if user doesnot provide input file
    else:
        inShapefile = argument[1]
        # Get the input Layer
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(inShapefile, 0)
    print inDataSource
    inLayer = inDataSource.GetLayer()
    print inLayer.GetFeatureCount()

    # Create the output Layer
    outShapefile = "multi-polygon.shp"
    outDriver = ogr.GetDriverByName("ESRI Shapefile")

    # Remove output shapefile if it already exists
    if os.path.exists(outShapefile):
        outDriver.DeleteDataSource(outShapefile)

    # Create the output shapefile
    outDataSource = outDriver.CreateDataSource(outShapefile)
    outLayer = outDataSource.CreateLayer("polygon", geom_type=ogr.wkbMultiPolygon)

    # Add input Layer Fields to the output Layer
    inLayerDefn = inLayer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        outLayer.CreateField(fieldDefn)

    idField = ogr.FieldDefn("Doors", ogr.OFTInteger)
    outLayer.CreateField(idField)
    # Get the output Layer's Feature Definition
    outLayerDefn = outLayer.GetLayerDefn()
    outFeature = ogr.Feature(outLayerDefn)
    wall_layer = inLayer
    wall_layer_tmp = inLayer
    #Create Multiple Polygon
    multipolygon = ogr.Geometry(ogr.wkbMultiPolygon)
    # Create polygon #1
    poly1 = ogr.Geometry(ogr.wkbPolygon)

    used=[]
    used2 = []

    flag=0
    #flag =0 neither i edge nor j have been detected, new polygon
    #flag =1 a polygon with initial edge
    #flag =2 the first edge has been used once
    #flag =3 two edges have been used, donot draw the polygon
    for i in range(0,wall_layer.GetFeatureCount()):
        count = 0
        wall_feat2 = wall_layer.GetFeature(i)
        wall_geom2 = wall_feat2.GetGeometryRef()
        flag=0
        id2=wall_feat2.GetFieldAsInteger("ID")
        for x in used:
            if x==id2:
                print "Done already"
                flag=1
                break
        for x in used2:
             if x == id2:
                print "Done as a subset"
                flag = 2
                break
        if(flag == 1):
            continue
        print "starting a ring"
        ring1 = ogr.Geometry(ogr.wkbLinearRing)
        used.append(id2)
        for j in range(0,wall_layer.GetFeatureCount()):
            wall_feat = wall_layer.GetFeature(j)
            id =  wall_feat.GetFieldAsInteger("ID")
            used2.append(id)
            if(id == id2):
                continue
            if(flag == 2):
                for x in used2:
                    if x == id:
                        print "This polygon has been detected before"
                        flag=3
                        break
                if(flag == 3):
                    break
            wall_geom = wall_feat.GetGeometryRef()
            type= wall_feat.GetFieldAsString("Type1")
            print type
            if type == "door":
                count=count+1
            arr = wall_geom.GetPoints()
            arr2= wall_geom2.GetPoints()
            print arr
            if (arr[0][0] == arr[1][0]) and (arr[0][1] == arr[1][1]) or (arr2[0][0] == arr2[1][0]) and (arr2[0][1] == arr2[1][1]):
                print "points"
            else:
                print "line"
                if (-0.01<(arr[0][0]-arr2[0][0])<0.01) or (-0.01<(arr[0][0] - arr2[1][0])<0.01) or (-0.01<(arr[1][0]-arr2[0][0])<0.01) or (-0.01<(arr[1][0]-arr2[1][0])<0.01):
                    print "yes"
                    ring1.AddPoint(arr[0][0],arr[0][1])
                    print ring1.ExportToWkt()

            print j,i
        if(flag == 0 or flag == 2):
            x=wall_layer.GetFeature(i)
            y=x.GetGeometryRef()
            z=y.GetPoints()
            ring1.AddPoint(z[0][0], z[0][1])
            poly1.AddGeometry(ring1)
            multipolygon.AddGeometry(poly1)

    print multipolygon.ExportToWkt()
    outFeature.SetGeometry(multipolygon)

    print count
    outFeature.SetField("Doors", count)
    outLayer.CreateFeature(outFeature)



    #wall_layer.ResetReading()
        # Add new feature to output Layer
     #   outLayer.CreateFeature(outFeature)

    # Close DataSources
    inDataSource.Destroy()
    outDataSource.Destroy()

main()