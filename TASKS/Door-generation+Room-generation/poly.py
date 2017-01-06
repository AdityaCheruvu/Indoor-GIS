from osgeo import ogr
import os

# Get the input Layer
inShapefile = "door.shp"
inDriver = ogr.GetDriverByName("ESRI Shapefile")
inDataSource = inDriver.Open(inShapefile, 0)
print inDataSource
inLayer = inDataSource.GetLayer()
print inLayer.GetFeatureCount()

# Create the output Layer
outShapefile = "polygon2.shp"
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

# Get the output Layer's Feature Definition
outLayerDefn = outLayer.GetLayerDefn()
outFeature = ogr.Feature(outLayerDefn)
wall_layer = inLayer
wall_layer_tmp = inLayer
# Create ring #1
ring1 = ogr.Geometry(ogr.wkbLinearRing)



# Create polygon #1
poly1 = ogr.Geometry(ogr.wkbPolygon)


for i in range(1,wall_layer.GetFeatureCount()):
    wall_feat = wall_layer.GetFeature(i-1)
    wall_feat2 = wall_layer.GetFeature(i)
    wall_geom = wall_feat.GetGeometryRef()
    wall_geom2 = wall_feat.GetGeometryRef()
    arr = wall_geom.GetPoints()
    arr2= wall_geom2.GetPoints()
    print arr
    if (arr[0][0] == arr[1][0]) and (arr[0][1] == arr[1][1]) or (arr2[0][0] == arr2[1][0]) and (arr2[0][1] == arr2[1][1]):
        print "points"
    else:
        print "line"
        if (-0.01<(arr[0][0]-arr2[0][0])<0.01) or (-0.01<(arr[0][0] - arr2[1][0])<0.01) or (-0.01<(arr[1][0]-arr2[0][0])<0.01) or (-0.01<(arr[1][0]-arr2[1][0])<0.01):
            print "yes"
            ring1.AddPoint(arr2[0][0],arr2[0][1])

    print i-1,i
x=wall_layer.GetFeature(0)
y=x.GetGeometryRef()
z=y.GetPoints()
print z
ring1.AddPoint(z[0][0], z[0][1])
poly1.AddGeometry(ring1)
outFeature.SetGeometry(poly1)
outLayer.CreateFeature(outFeature)


#wall_layer.ResetReading()
    # Add new feature to output Layer
 #   outLayer.CreateFeature(outFeature)

# Close DataSources
#inDataSource.Destroy()
#outDataSource.Destroy()