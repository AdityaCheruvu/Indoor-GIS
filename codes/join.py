from osgeo import ogr
from point_at_dist import point_at_dist, perpendicular_point
import os
v = "vindhya_algo_test_lin.shp"
file_name = v  # Name of the shapefile

def join_line():
    # Create center line

    # Get the parallel lines with between distance

    driver = ogr.GetDriverByName('ESRI Shapefile')

    shapefile_name = 'cente_line_shp/myline.shp'
    if os.path.exists(shapefile_name):
        driver.DeleteDataSource(shapefile_name)

    out_data_source = driver.CreateDataSource(shapefile_name)

    # Create Layer

    out_layer = out_data_source.CreateLayer('join_center_line', geom_type=ogr.wkbLineString)

    # Set Geometry

    out_layer_defn = out_layer.GetLayerDefn()

    wall_data = driver.Open(file_name, update=True)
    wall_layer = wall_data.GetLayerByIndex(0)
    wall_layer_defn = wall_layer.GetLayerDefn()

    wall_data_tmp = driver.Open(file_name, update=True)
    wall_layer_tmp = wall_data_tmp.GetLayerByIndex(0)
    cline_done = []
    print "Case 1 starting"
    for wall_feature in wall_layer:

        wall_geom = wall_feature.GetGeometryRef()
        id1 = wall_feature.GetFieldAsInteger("ID")
        wall_layer_tmp.ResetReading()


        for wall_feature_tmp in wall_layer_tmp:
            wall_tmp_geom = wall_feature_tmp.GetGeometryRef()
            id2 = wall_feature_tmp.GetFieldAsInteger("ID")
            if is_within_distance(wall_geom, wall_tmp_geom) and id1 != id2 and [id1, id2] not in cline_done and [id2, id1] not in cline_done:
                print 'case1 first if'
                cline_info = get_join_line(wall_geom, wall_tmp_geom)
                print cline_info
                if cline_info[0]:

                    new_geom = create_line(cline_info[1])
                    feature = ogr.Feature(out_layer_defn)
                    feature.SetGeometry(new_geom)
                    out_layer.CreateFeature(feature)
                    feature.Destroy()

                    print wall_geom.Distance(wall_tmp_geom)
                    print id1, id2, 'yes wall line First method'
                    print
                    cline_done.append([id1, id2])

    out_data_source.Destroy()
    wall_data.Destroy()
    wall_data_tmp.Destroy()



def create_line(points):
    """

    :param points: array of points
    :return: geometry of line
    """
    line = ogr.Geometry(ogr.wkbLineString)

    for pt in points:
        print pt
        print "YOGOGOGOGOGOGOGOGOGOOG"
        line.AddPoint(pt)
    return line







def is_within_distance(geom1, geom2):
    """

    :param geom1: geometry of first line
    :param geom2: geometry of second line
    :return: True if within distance else False
    """
    points1 = geom1.GetPoints()
    point1a=points1[0]
    point1b=points1[1]

    points2 = geom2.GetPoints()
    point2a=points2[0]
    point2b=points2[1]


    if geom1.Distance(geom2) <=.0001:
        return True
    else:
        return False






def get_join_line(geom1, geom2):
    points1 = geom1.GetPoints()
    point1a = points1[0]
    point1b = points1[1]

    points2 = geom2.GetPoints()
    point2a = points2[0]
    point2b = points2[1]


    pg=[]
    pg.append(ogr.Geometry(ogr.wkbPoint))
    pg.append(ogr.Geometry(ogr.wkbPoint))
    pg.append(ogr.Geometry(ogr.wkbPoint))
    pg.append(ogr.Geometry(ogr.wkbPoint))



    pg[0].AddPoint(point1a[0],point1a[1])
    pg[1].AddPoint(point1b[0],point1b[1])
    pg[2].AddPoint(point2a[0],point2a[1])
    pg[3].AddPoint(point2b[0],point2b[1])

    dist=[]
    dist.append(pg[0].Distance(pg[2]))
    dist.append(pg[0].Distance(pg[3]))
    dist.append(pg[1].Distance(pg[2]))
    dist.append(pg[1].Distance(pg[3]))

    mindist=min(dist)
    for i in range(4):
        if dist[i] == mindist:
            return True,[pg[i/2],pg[(i%2)+2]]
    return False,[]



if __name__ == '__main__':
    join_line()
