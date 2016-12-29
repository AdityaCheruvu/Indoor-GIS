import ogr, os

# Input data
pointCoord = -124.4577,48.0135
point2Coord = -224.4577,48.0135
point3Coord = -124.4577,0.0135
fieldName = 'TYPE'
fieldType = ogr.OFTString
corridorValue = 'corridor'
codoorValue = 'codoor'
doorValue = 'door'
centroidValue = 'centroid'
outSHPfn = 'points.shp'

# Create the output shapefile
shpDriver = ogr.GetDriverByName("ESRI Shapefile")
if os.path.exists(outSHPfn):
    shpDriver.DeleteDataSource(outSHPfn)
outDataSource = shpDriver.CreateDataSource(outSHPfn)
outLayer = outDataSource.CreateLayer(outSHPfn, geom_type=ogr.wkbPoint )

#create point geometry
point = ogr.Geometry(ogr.wkbPoint)
point.AddPoint(pointCoord[0],pointCoord[1])
point2 = ogr.Geometry(ogr.wkbPoint)
point2.AddPoint(point2Coord[0],point2Coord[1])
point3 = ogr.Geometry(ogr.wkbPoint)
point3.AddPoint(point3Coord[0],point3Coord[1])

# create a field
idField = ogr.FieldDefn(fieldName, fieldType)
outLayer.CreateField(idField)

# Create the feature and set values
featureDefn = outLayer.GetLayerDefn()
outFeature = ogr.Feature(featureDefn)

outFeature.SetGeometry(point)
outFeature.SetField(fieldName, corridorValue)
outLayer.CreateFeature(outFeature)



outFeature.SetGeometry(point2)
outFeature.SetField(fieldName, codoorValue)
outLayer.CreateFeature(outFeature)

outFeature.SetGeometry(point3)
outFeature.SetField(fieldName, centroidValue)
outLayer.CreateFeature(outFeature)


outFeature = None