from osgeo import ogr
import os

# Get the input Layer
inShapefile = "points.shp"
inDriver = ogr.GetDriverByName("ESRI Shapefile")
inDataSource = inDriver.Open(inShapefile, 0)
inLayer = inDataSource.GetLayer()

# Create the output Layer
outShapefile = "lines.shp"
outDriver = ogr.GetDriverByName("ESRI Shapefile")

# Remove output shapefile if it already exists
if os.path.exists(outShapefile):
    outDriver.DeleteDataSource(outShapefile)

# Create the output shapefile
outDataSource = outDriver.CreateDataSource(outShapefile)
outLayer = outDataSource.CreateLayer("lines", geom_type=ogr.wkbLineString)

# Add input Layer Fields to the output Layer
inLayerDefn = inLayer.GetLayerDefn()
for i in range(0, inLayerDefn.GetFieldCount()):
    fieldDefn = inLayerDefn.GetFieldDefn(i)
    outLayer.CreateField(fieldDefn)

# Get the output Layer's Feature Definition
outLayerDefn = outLayer.GetLayerDefn()
outFeature = ogr.Feature(outLayerDefn)
line = ogr.Geometry(ogr.wkbLineString)

geom=[]
print inLayer.GetFeatureCount()
# Add features to the ouput Layer
for i in range(0, inLayer.GetFeatureCount()):
    # Get the input Feature
    inFeature = inLayer.GetFeature(i)
    # Create output Feature
    # Add field values from input Layer
    for i in range(0, outLayerDefn.GetFieldCount()):
        outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i))

    geom.append(inFeature.GetGeometryRef().GetPoints())
    print geom

    print geom[i]
    line.AddPoint(geom[i][0][0], geom[i][0][1])

print line.ExportToWkt()
outFeature.SetGeometry(line)
print outFeature
# Add new feature to output Layer
outLayer.CreateFeature(outFeature)

outFeature = None

# Close DataSources

inDataSource.Destroy()
outDataSource.Destroy()