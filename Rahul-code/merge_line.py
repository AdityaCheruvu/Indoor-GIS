from osgeo import ogr
from point_at_dist import point_at_dist, perpendicular_point
import os

# Please set these variables
v = "vindhya_algo_test_lin.shp"
c = "1roomr.shp"
t = "1roomw.shp"
file_name = t  # Name of the shapefile

# In meters
min_wall_width = 1
max_wall_width = 13.5


def clean_shp_file():
    driver = ogr.GetDriverByName('ESRI Shapefile')

    wall_data = driver.Open(file_name, update=True)
    wall_layer = wall_data.GetLayerByIndex(0)
    wall_layer_defn = wall_layer.GetLayerDefn()

    wall_data_tmp = driver.Open(file_name, update=True)
    wall_layer_tmp = wall_data_tmp.GetLayerByIndex(0)
    #opened the file twice

    count = 0
    duplicate_id = []
    max_feature_value = -1
    # Clean the Overlapping

    for wall_feature in wall_layer:
        wall_geom = wall_feature.GetGeometryRef()
        id1 = wall_feature.GetFieldAsInteger("ID")
        # getting max id value; used in next section
        if max_feature_value < id1:
            max_feature_value = id1
        wall_layer_tmp.ResetReading() #goes back to 0 index
        for wall_feature_tmp in wall_layer_tmp:
            wall_tmp_geom = wall_feature_tmp.GetGeometryRef()
            id2 = wall_feature_tmp.GetFieldAsInteger("ID")

            if id1 != id2 and id1 not in duplicate_id and id2 not in duplicate_id:
                # Deletes the overlapping

                if wall_geom.Contains(wall_tmp_geom):
                    print 'contains'
                    duplicate_id.append(wall_feature_tmp.GetFieldAsInteger("ID"))
                    wall_layer.DeleteFeature(wall_feature_tmp.GetFID())
                elif wall_tmp_geom.Contains(wall_geom):
                    print 'contains otherwise'
                    duplicate_id.append(wall_feature.GetFieldAsInteger("ID"))
                    wall_layer.DeleteFeature(wall_feature.GetFID())
                # Delete the overlapping but with minute distance shifted
                else:
                    wall_tmp_points = wall_tmp_geom.GetPoints()
                    wall_points = wall_geom.GetPoints()
                    # print wall_geom.Distance(get_geom_point(wall_tmp_points[0]))
                    # print wall_geom.Distance(get_geom_point(wall_tmp_points[-1]))

                    if wall_geom.Distance(get_geom_point(wall_tmp_points[0])) < 0.001 and wall_geom.Distance(
                            get_geom_point(wall_tmp_points[-1])) < 0.001:
                        duplicate_id.append(wall_feature_tmp.GetFieldAsInteger("ID"))
                        wall_layer.DeleteFeature(wall_feature_tmp.GetFID())
                    # print wall_tmp_geom.Distance(get_geom_point(wall_points[0]))
                    # print wall_tmp_geom.Distance(get_geom_point(wall_points[-1]))
                    elif wall_tmp_geom.Distance(get_geom_point(wall_points[0])) < 0.1 and wall_tmp_geom.Distance(
                            get_geom_point(wall_points[-1])) < 0.1:
                        duplicate_id.append(wall_feature.GetFieldAsInteger("ID"))
                        wall_layer.DeleteFeature(wall_feature.GetFID())

    print len(duplicate_id), ': lines deleted'


    # Join the overlapping
    # TODO add the slope factor and also fix if multiple are joining
    fixed_list = []

    joined = -1

    #
    while_count = 0
    total_joined = 0
    # Run as many time till all the one point touching or overlapping are merged into one line
    while joined:
        wall_data.Destroy()
        # Opening again and again because of changing the shapefile and two iterator
        wall_data = driver.Open(file_name, update=True)
        wall_layer = wall_data.GetLayerByIndex(0)
        wall_layer_defn = wall_layer.GetLayerDefn()

        joined = 0
        print '\nwhile : ', while_count
        while_count += 1
        wall_layer.ResetReading()

        for wall_feature in wall_layer:
            wall_geom = wall_feature.GetGeometryRef()
            id1 = wall_feature.GetFieldAsInteger("ID")
            wall_data_tmp.Destroy()
            wall_data_tmp = driver.Open(file_name, update=True)
            wall_layer_tmp = wall_data_tmp.GetLayerByIndex(0)
            for wall_feature_tmp in wall_layer_tmp:
                wall_tmp_geom = wall_feature_tmp.GetGeometryRef()
                id2 = wall_feature_tmp.GetFieldAsInteger("ID")
                # Merging the broken or semi-overlapping lines
                if is_parallel(wall_geom, wall_tmp_geom) and id1 != id2 and [id1, id2] not in fixed_list and [id2, id1] not in fixed_list:
                    fixed_list.append([id1, id2])
                    wall_tmp_points = wall_tmp_geom.GetPoints()
                    if wall_geom.Distance(get_geom_point(wall_tmp_points[0])) < 0.001 or wall_geom.Distance(
                            get_geom_point(wall_tmp_points[-1])) < 0.001:
                        joined += 1
                        total_joined += 1
                        new_geom = merge_geom(wall_geom, wall_tmp_geom)
                        new_feature = ogr.Feature(wall_layer_defn)
                        for i in range(0, wall_layer_defn.GetFieldCount()):
                            if wall_layer_defn.GetFieldDefn(i).GetNameRef() == "ID":
                                max_feature_value += 1
                                new_feature.SetField(wall_layer_defn.GetFieldDefn(i).GetNameRef(), max_feature_value)
                            else:
                                new_feature.SetField(wall_layer_defn.GetFieldDefn(i).GetNameRef(), wall_feature.GetField(i))

                        # Delete the disjoint geom
                        wall_layer.DeleteFeature(wall_feature_tmp.GetFID())
                        wall_layer.DeleteFeature(wall_feature.GetFID())

                        # Add the new, joined geom
                        new_feature.SetGeometry(new_geom)
                        wall_layer.CreateFeature(new_feature)

            print joined, " : joined in this iteration"
    print total_joined, " : Total Joined"


def create_center_line():
    # Create center line

    # Get the parallel lines with between distance

    driver = ogr.GetDriverByName('ESRI Shapefile')

    shapefile_name = 'cente_line_shp/cline.shp'
    if os.path.exists(shapefile_name):
        driver.DeleteDataSource(shapefile_name)

    out_data_source = driver.CreateDataSource(shapefile_name)

    # Create Layer

    out_layer = out_data_source.CreateLayer('center_line', geom_type=ogr.wkbLineString)

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
            if is_parallel(wall_geom, wall_tmp_geom) and id1 != id2 and [id1, id2] not in cline_done and [id2, id1] not in cline_done:
                print 'case1 first if'
                if is_wall_lines(wall_geom, id1, wall_tmp_geom, id2, False):
                    print 'case1 second if'
                    cline_info = get_center_line(wall_geom, wall_tmp_geom)
                    print cline_info
                    #  print "LOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOk here"
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

    wall_layer.ResetReading()
    print "Case 2 Starting"
    for wall_feature in wall_layer:

        wall_geom = wall_feature.GetGeometryRef()
        id1 = wall_feature.GetFieldAsInteger("ID")
        wall_layer_tmp.ResetReading()

        for wall_feature_tmp in wall_layer_tmp:
            wall_tmp_geom = wall_feature_tmp.GetGeometryRef()
            id2 = wall_feature_tmp.GetFieldAsInteger("ID")
            if is_parallel(wall_geom, wall_tmp_geom) and id1 != id2 and [id1, id2] not in cline_done and [id2, id1] not in cline_done:
                if is_wall_lines(wall_geom, id1, wall_tmp_geom, id2, True):
                    cline_info = get_center_line(wall_geom, wall_tmp_geom)
                    if cline_info[0]:
                        new_geom = create_line(cline_info[1])
                        feature = ogr.Feature(out_layer_defn)
                        feature.SetGeometry(new_geom)
                        out_layer.CreateFeature(feature)
                        feature.Destroy()
                        print wall_geom.Distance(wall_tmp_geom)
                        print id1, id2, 'yes wall line : Second method'
                        print
                        cline_done.append([id1, id2])
    out_data_source.Destroy()
    wall_data.Destroy()
    wall_data_tmp.Destroy()


def merge_geom(geom1, geom2):
    """
    :param geom1: OgrGeometry
    :param geom2: OgrGeometry

    :return: merged geometry
    """
    points1 = geom1.GetPoints()
    points2 = geom2.GetPoints()
    # print points1, points2
    tmp_distance = -1
    new_geom_point = []
    for p1 in points1:
        for p2 in points2:
            if tmp_distance < distance_between(p1, p2):
                new_geom_point = [p1, p2]
                tmp_distance = distance_between(p1, p2)
                # print new_geom_point
    return create_line(new_geom_point)


def create_line(points):
    """

    :param points: array of points
    :return: geometry of line
    """
    line = ogr.Geometry(ogr.wkbLineString)

    for pt in points:
        line.AddPoint(float(pt[0]), float(pt[1]))
    return line


def get_geom_point(pt):
    """

    :param pt: array with [x,y]
    :return: return OgrPoint using x,y
    """
    pt_ = ogr.Geometry(ogr.wkbPoint)
    pt_.AddPoint(float(pt[0]), float(pt[1]))
    return pt_


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


def is_parallel(geom1, geom2):
    """

    :param geom1: geometry of first line
    :param geom2: geometry of second line
    :return: True if parallel else False
    """
    points1 = geom1.GetPoints()
    points2 = geom2.GetPoints()
    print "Geom1"
    print geom1
    print "Geom2"
    print geom2

    if -.01 < (points1[0][0] - points1[1][0]) < .01 and -.01 < (points2[0][0] - points2[1][0]) < .01:
        return True #vertical lines, slopes cannot be calculated
    elif -.01 < (points1[0][0] - points1[1][0]) < .01 or -.01 < (points2[0][0] - points2[1][0]) < .01:
        return False

    s1 = (points1[0][1] - points1[1][1]) / (points1[0][0] - points1[1][0]) #y2-y1/x2-x1
    s2 = (points2[0][1] - points2[1][1]) / (points2[0][0] - points2[1][0])

    if -0.00000001 < s1-s2 < .00000001:
        print "True"
        return True
    else:
        print "False"
        return False


def is_wall_lines(geom1, id1, geom2, id2, no_common_ending_check):
    if min_wall_width <= geom1.Distance(geom2) <= max_wall_width: #make sure the parallel lines are making a wall
        # Check First scenario as Common wall where both are ending
        if no_common_ending_check:
            return True
        if is_common_ending(geom1, id1, geom2, id2):
            return True
        # Check second scenario as continuing/Joining lines are parallel
        # else is_extending(geom1, id1, geom2, id2):
        #     return [True, 2, common]
    else:
        return False


def is_common_ending(geom1, id1, geom2, id2):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    wall_data = driver.Open(file_name, update=True)
    wall_layer = wall_data.GetLayerByIndex(0)
    for feature in wall_layer:
        geom = feature.GetGeometryRef()
        id = feature.GetFieldAsInteger("ID")
        if id != id1 and id != id2 and geom.Distance(geom1) <= .0001 and geom.Distance(geom2) <= .00001:
            print id, ' : Id is common for ', id1, ' and ', id2
            return True
    return False


def get_center_line(geom1, geom2):
    print "GET Center line Started"
    points1 = geom1.GetPoints()
    points2 = geom2.GetPoints()

    p10 = perpendicular_point(points1[0], points1[1], points1[0])
    p11 = perpendicular_point(points1[0], points1[1], points1[1])
    pair10 = point_at_dist(points1[0], p10, 500)
    pair11 = point_at_dist(points1[1], p11, 500)
    p_line10 = create_line(pair10)
    p_line11 = create_line(pair11)

    p20 = perpendicular_point(points2[0], points2[1], points2[0])
    p21 = perpendicular_point(points2[0], points2[1], points2[1])
    pair20 = point_at_dist(points2[0], p20, 500)
    pair21 = point_at_dist(points2[1], p21, 500)
    p_line20 = create_line(pair20)
    p_line21 = create_line(pair21)

    # case1 : geom1 is small and completely covered by geom2
    if p_line10.Distance(p_line11) > max_wall_width and p_line10.Distance(geom2) < .0001 and p_line11.Distance(geom2) < 0.0001:
        print "case1"
        print points1
        return generate_center_line(points1, [intersection_point(pair10, points2), intersection_point(pair11, points2)])
        # return [True, [intersection_point(pair10, points2), intersection_point(pair11, points2)]]
    # case2 : geom2 is small and completely covered by geom1
    elif p_line20.Distance(p_line21) > max_wall_width and p_line20.Distance(geom1) < .0001 and p_line21.Distance(geom1) < 0.0001:
        print "case2"
        return generate_center_line(points2, [intersection_point(pair20, points1), intersection_point(pair21, points1)])
    # case3 : between both the line
    elif p_line10.Distance(p_line20) > max_wall_width and p_line10.Distance(geom2) < .0001 and p_line20.Distance(geom1) < 0.001:
        print "case3-1"
        return generate_center_line([points1[0], intersection_point(pair20, points1)], [intersection_point(points2, pair10), points2[0]])
    elif p_line10.Distance(p_line21) > max_wall_width and p_line10.Distance(geom2) < .0001 and p_line21.Distance(geom1) < 0.0001:
        print "case3-2"
        return generate_center_line([points1[0], intersection_point(pair21, points1)], [intersection_point(points2, pair10), points2[1]])
    elif p_line11.Distance(p_line20) > max_wall_width and p_line11.Distance(geom2) < .0001 and p_line20.Distance(geom1) < 0.001:
        print "case3-3"
        return generate_center_line([points1[1], intersection_point(pair20, points1)], [intersection_point(points2, pair11), points2[0]])
    elif p_line11.Distance(p_line21) > max_wall_width and p_line11.Distance(geom2) < .0001 and p_line21.Distance(geom1) < 0.0001:
        print "case3-4"
        return generate_center_line([points1[1], intersection_point(pair21, points1)], [intersection_point(points2, pair11), points2[1]])
    else:
        return [False, []]


def intersection_point(line1, line2):
    x1, y1, x2, y2 = line1[0] + line1[1]
    x3, y3, x4, y4 = line2[0] + line2[1]

    # Check if line is parallel
    denominator = (x1 - x2)*(y3-y4) - (y1-y2)*(x3-x4)
    if denominator == 0.0:
        return ()

    intersection = (((x1*y2 - y1*x2)*(x3-x4) - (x1 - x2)*(x3*y4 - y3*x4)) / denominator,
                    ((x1*y2 - y1*x2)*(y3-y4) - (y1 - y2)*(x3*y4 - y3*x4)) / denominator)

    return intersection


def generate_center_line(line1, line2):
    x1, y1 = tuple((x + y) / 2.0 for x, y in zip(line1[0], line2[0]))
    x2, y2 = tuple((x + y) / 2.0 for x, y in zip(line1[1], line2[1]))
    return [True, [(x1, y1), (x2, y2)]]


def create_center_line_shapefile(geom, name):

    out_driver = ogr.GetDriverByName("ESRI Shapefile")
    shapefile_name = 'cente_line_shp/%s' % name
    if os.path.exists(shapefile_name):
        out_driver.DeleteDataSource(shapefile_name)

    out_data_source = out_driver.CreateDataSource(shapefile_name)

    # Create Layer

    out_layer = out_data_source.CreateLayer('center_line', geom_type=ogr.wkbLineString)

    # Set Geometry

    out_layer_defn = out_layer.GetLayerDefn()
    feature = ogr.Feature(out_layer_defn)
    feature.SetGeometry(geom)

    # Create Feature

    out_layer.CreateFeature(feature)
    feature.Destroy()

    # Destroy Feature
    out_data_source.Destroy()


if __name__ == '__main__':
    clean_shp_file()
    create_center_line()
