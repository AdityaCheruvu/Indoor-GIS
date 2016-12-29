from osgeo import ogr
import os

# Get the input Layer
inShapefile = "1roomr.shp"
inDriver = ogr.GetDriverByName("ESRI Shapefile")
inDataSource = inDriver.Open(inShapefile, 0)
inLayer = inDataSource.GetLayer()

# Create the output Layer
outShapefile = "centroids.shp"
outDriver = ogr.GetDriverByName("ESRI Shapefile")

# Remove output shapefile if it already exists
if os.path.exists(outShapefile):
    outDriver.DeleteDataSource(outShapefile)

# Create the output shapefile
outDataSource = outDriver.CreateDataSource(outShapefile)
outLayer = outDataSource.CreateLayer("centroid", geom_type=ogr.wkbPoint)


# Add input Layer Fields to the output Layer
inLayerDefn = inLayer.GetLayerDefn()
for i in range(0, inLayerDefn.GetFieldCount()):
    fieldDefn = inLayerDefn.GetFieldDefn(i)
    outLayer.CreateField(fieldDefn)
idField = ogr.FieldDefn("Type", ogr.OFTString)
outLayer.CreateField(idField)

# Get the output Layer's Feature Definition
outLayerDefn = outLayer.GetLayerDefn()

# Add features to the ouput Layer
for i in range(0, inLayer.GetFeatureCount()):
    # Get the input Feature
    inFeature = inLayer.GetFeature(i)
    # Create output Feature
    outFeature = ogr.Feature(outLayerDefn)
    # Set geometry as centroid
    geom = inFeature.GetGeometryRef()
    centroid = geom.Centroid()

    outFeature.SetGeometry(centroid)
    outFeature.SetField("Type", "room-centroid")
    # Add new feature to output Layer
    outLayer.CreateFeature(outFeature)

# Close DataSources
inDataSource.Destroy()
outDataSource.Destroy()