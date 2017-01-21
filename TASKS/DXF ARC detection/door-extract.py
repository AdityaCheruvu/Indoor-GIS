import ezdxf
import sys
def main():
    argument = sys.argv
    FileName="VindhyaModelization.dxf"
    #default filename if nothing else is mentioned
    if not (len(argument)==2) :
        print "Usage: python ExtractLine.py Filename"
        sys.exit()
    FileName = argument[1]
    dwg = ezdxf.readfile(FileName)
    modelspace = dwg.modelspace()
    arcs = modelspace.query('ARC')
    for a in arcs:
        print "door detected"
        print a.center
        #prints center of the arc
        print a.radius
        print a.start_angle
        print a.end_angle
        #prints radius, start_angle, end_angle of the arc, can be used to find door center

main()