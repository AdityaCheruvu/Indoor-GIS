from osgeo import ogr
import os

# Get the input Layer
inShapefile = "polygon2.shp"
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
idField = ogr.FieldDefn("Geometry", ogr.OFTString)
outLayer.CreateField(idField)
idField = ogr.FieldDefn("Capacity", ogr.OFTInteger)
outLayer.CreateField(idField)
idField = ogr.FieldDefn("Impedence", ogr.OFTReal)
outLayer.CreateField(idField)
idField = ogr.FieldDefn("Distances", ogr.OFTInteger)
outLayer.CreateField(idField)
idField = ogr.FieldDefn("Openings", ogr.OFTInteger)
outLayer.CreateField(idField)
idField = ogr.FieldDefn("Attribute7", ogr.OFTString)
outLayer.CreateField(idField)
idField = ogr.FieldDefn("Attribute8", ogr.OFTString)
outLayer.CreateField(idField)
idField = ogr.FieldDefn("Attribute9", ogr.OFTString)
outLayer.CreateField(idField)
idField = ogr.FieldDefn("Attribute0", ogr.OFTString)
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
    doors= inFeature.GetFieldAsInteger("Doors")
    centroid = geom.Centroid()
    print centroid
    outFeature.SetGeometry(centroid)
    outFeature.SetField("Type", "room-centroid")
    outFeature.SetField("Geometry", "Polygon")
    outFeature.SetField("Capacity", 10)
    outFeature.SetField("Impedence", 0.34)
    outFeature.SetField("Distances", 3)
    outFeature.SetField("Openings", doors)
    print doors
    outFeature.SetField("Attribute7", "Test-data")
    outFeature.SetField("Attribute8", "Test-data")
    outFeature.SetField("Attribute9", "Test-data")
    outFeature.SetField("Attribute0", "Test-data")
    # Add new feature to output Layer
    outLayer.CreateFeature(outFeature)

# Close DataSources
inDataSource.Destroy()
outDataSource.Destroy()