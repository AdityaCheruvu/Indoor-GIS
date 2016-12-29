# to find point B on line at distance D from point A on same line
import sys
from sympy import *
from fractions import Fraction

def point_at_dist(pt1, pt2, distance):

    if pt1 == pt2:
        print 'invalid line'
        sys.exit()

    # Check for slop 0 and infinite

    if pt1[0] == pt2[0]:
        p1, p2, p3, p4 = (pt1[0], pt1[1]+distance), (pt1[0], pt1[1]-distance), (pt2[0], pt2[1]+distance),\
                         (pt2[0], pt2[1]-distance)
        return [p1, p2, p3, p4]

    elif pt1[1] == pt2[1]:
        p1, p2, p3, p4 = (pt1[0]+distance, pt1[1]), (pt1[0]-distance, pt1[1]), (pt2[0]+distance, pt2[1]),\
                         (pt2[0]-distance, pt2[1])
        return [p1, p2, p3, p4]

    m = (pt1[1]-pt2[1])/(pt1[0]-pt2[0])

    p1 = (pt1[0] + dx(distance, m), pt1[1] + dy(distance, m))
    p2 = (pt1[0] - dx(distance, m), pt1[1] - dy(distance, m))

    p3 = (pt2[0] + dx(distance, m), pt2[1] + dy(distance, m))
    p4 = (pt2[0] - dx(distance, m), pt2[1] - dy(distance, m))

    return [p1, p2, p3, p4]


def dy(distance, m):
    return m*dx(distance, m)


def dx(distance, m):
    return distance/sqrt((m**2+1))


def perpendicular_point(stp, ep, p):
    d1, d2 = tuple(x-y for x, y in zip(stp, ep))
    if d2 == 0:  # If a horizontal line
        if p[1] == stp[1]:  # if p is on this linear entity
            # print p
            # print tuple(x+y for x, y in zip(p, (0.0, 100.0)))
            return tuple(x+y for x, y in zip(p, (0.0, 100.0)))
        else:
            p2 = (p[0], stp[1])
            return p2
    else:
        p2 = (p[0] - d2, p[1] + d1)
        return p2

if __name__ == '__main__':
    points = point_at_dist((1.0, 1.0), (2.0, 4.0), 10.0/9.0)
    print points
    # points = point_at_dist((1.0, 1.0), (1.0, 4.0), 5.0)
    # print points
    # points = point_at_dist((1.0, 1.0), (2.0, 1.0), 5.0)
    # print points
    print sqrt(5)