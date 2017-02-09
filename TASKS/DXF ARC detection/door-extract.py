import ezdxf
import sys
def main():
    argument = sys.argv
    #default filename if nothing else is mentioned
    if not (len(argument)==2) :
        print "Usage: python ExtractLine.py Filename"
        FileName = "VindhyaModelization.dxf"
    else:
        FileName = argument[1]
    dwg = ezdxf.readfile(FileName)
    modelspace = dwg.modelspace()
    for w in modelspace:
        print w.dxftype()
        print w
    arcs = modelspace.query('ARC')
    lines = modelspace.query('LINE')
    for a in arcs:
        for l in lines:
            s=l.dxf.start;
            e=l.dxf.end;
            c=a.center;
            r=a.radius;
            if(s==c or e==c ) and abs(s-e)==r: #if the detected line has one of its endpoints as one of the arc endpoints and
                                                #its length matches the radius of the arc, then the arc is a part of a door
                print "door detected"
                break
        #for debugging
        print a.center
        print a.radius
        print a.start_angle
        print a.end_angle
        #prints radius, start_angle, end_angle of the arc, can be used to find door center

main()