#!/usr/bin/env python

# External Imports
import os
import sys
import math
import xml.etree.ElementTree as ET

# Local Imports
from . import shapes as shapes_pkg
from .shapes import point_generator
from .config import *

DEBUGGING = True
SVG = set(['rect', 'circle', 'ellipse', 'line', 'polyline', 'polygon', 'path'])


def generate_gcode(filename):
    ''' The main method that converts svg files into gcode files.
        Still incomplete. See tests/start.svg'''

    # Check File Validity
    if not os.path.isfile(filename):
        raise ValueError("File \""+filename+"\" not found.")

    if not filename.endswith('.svg'):
        raise ValueError("File \""+filename+"\" is not an SVG file.")

    # Define the Output
    # ASSUMING LINUX / OSX FOLDER NAMING STYLE
    log = ""
    log += debug_log("Input File: "+filename)

    dir_string, file = os.path.split(filename)

    # Make Output File
    outdir = dir_string + "/gcode_output/"
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    outfile = outdir + file.split(".svg")[0] + '.gcode'
    log += debug_log("Output File: "+outfile)

    # Make Debug File
    debugdir = dir_string + "/log/"
    if not os.path.exists(debugdir):
        os.makedirs(debugdir)
    debug_file = debugdir + file.split(".svg")[0] + '.log'
    log += debug_log("Log File: "+debug_file+"\n")

    # Get the SVG Input File
    file = open(filename, 'r')
    tree = ET.parse(file)
    root = tree.getroot()
    file.close()
    
    # Get the Height and Width from the parent svg tag
    width = root.get('width')
    height = root.get('height')
    if width == None or height == None:
        viewbox = root.get('viewBox')
        if viewbox:
            _, _, width, height = viewbox.split()                

    if width == None or height == None:
        # raise ValueError("Unable to get width or height for the svg")
        print("Unable to get width and height for the svg")
        sys.exit(1)
    
    # Scale the file appropriately
    # (Will never distort image - always scales evenly)
    # ASSUMES: Y ASIX IS LONG AXIS
    #          X AXIS IS SHORT AXIS
    # i.e. laser cutter is in "portrait"
    scale_x = bed_max_x / float(width)
    scale_y = bed_max_y / float(height)
    scale = min(scale_x, scale_y)
    if scale > 1:
        scale = 1


    log += debug_log("wdth: "+str(width))
    log += debug_log("hght: "+str(height))
    log += debug_log("scale: "+str(scale))
    log += debug_log("x%: "+str(scale_x))
    log += debug_log("y%: "+str(scale_y))

    # CREATE OUTPUT VARIABLE
    gcode = ""

    # Write Initial G-Codes
    gcode += preamble + "\n"
    gcode += "G1 F" + str(feed_rate) + "\n"
    
    # Iterate through svg elements
    for elem in root.iter():
        log += debug_log("--Found Elem: "+str(elem))
        new_shape = True
        try:
            tag_suffix = elem.tag.split("}")[-1]
        except:
            print("Error reading tag value:", tag_suffix)
            continue
        
        # Checks element is valid SVG shape
        if tag_suffix in SVG:

            log += debug_log("  --Name: "+str(tag_suffix))

            # Get corresponding class object from 'shapes.py'
            shape_class = getattr(shapes_pkg, tag_suffix)
            shape_obj = shape_class(elem)

            log += debug_log("\tClass : "+str(shape_class))
            log += debug_log("\tObject: "+str(shape_obj))
            log += debug_log("\tAttrs : "+str(list(elem.items())))
            log += debug_log("\tTransform: "+str(elem.get('transform')))


            ############ HERE'S THE MEAT!!! #############
            # Gets the Object path info in one of 2 ways:
            # 1. Reads the <tag>'s 'd' attribute.
            # 2. Reads the SVG and generates the path itself.
            d = shape_obj.d_path()
            log += debug_log("\td: "+str(d))

            # The *Transformation Matrix* #
            # Specifies something about how curves are approximated
            # Non-essential - a default is used if the method below
            #   returns None.
            m = shape_obj.transformation_matrix()
            log += debug_log("\tm: "+str(m))

            if d:
                log += debug_log("\td is GOOD!")

                gcode += shape_preamble + "\n"
                points = point_generator(d, m, smoothness)

                log += debug_log("\tPoints: "+str(points))
                #plist = list(points)
                #print(plist)

                x_prev, y_prev, x_curr, y_curr = None, None, None, None
                
                for x,y in points:

                    #log += debug_log("\t  pt: "+str((x,y)))

                    if x_curr is None:
                        x_curr = scale*x
                        y_curr = bed_max_y - scale*y

                    x_prev = x_curr
                    y_prev = y_curr

                    x_curr = scale*x
                    y_curr = bed_max_y - scale*y
                    z = math.sqrt((math.pow(x_prev-x_curr, 2) + math.pow(y_prev-y_curr, 2)))
                    #print()
                    #print("E-NUMBER BABY!:", z)

                    # Set the extrusion value (Ennn) per 10mm/1cm of lateral travel
                    b = z * extrusion_multi

                    # Increase material extruded cumulatively
                    if not 'e' in locals():
                        e = b
                    else:
                        e = e + b

                    print("X:", x_curr, "Y:", y_curr, "New_Extr:", e)
                    log += debug_log("\t  pt: "+str((x,y)))

                    if x >= 0 and x <= bed_max_x and y >= 0 and y <= bed_max_y:
                        if new_shape:
                            gcode += ("G0 X%0.3f Y%0.3f\n" % (x, y))
                            new_shape = False
                        else:

                            gcode += ("G1 X%0.3f Y%0.3f E%0.3f\n" % (x, y, e))
                        log += debug_log("\t    --Point printed")
                    else:
                        log += debug_log("\t    --POINT NOT PRINTED ("+str(bed_max_x)+","+str(bed_max_y)+")")
                gcode += shape_postamble + "\n"
            else:
              log += debug_log("\tNO PATH INSTRUCTIONS FOUND!!")
        else:
          log += debug_log("  --No Name: "+tag_suffix)

    gcode += postamble + "\n"

    # Write the Result
    ofile = open(outfile, 'w+')
    ofile.write(gcode)
    ofile.close()

    # Write Debugging
    if DEBUGGING:
        dfile = open(debug_file, 'w+')
        dfile.write(log)
        dfile.close()



def debug_log(message):
    ''' Simple debugging function. If you don't understand 
        something then chuck this frickin everywhere. '''
    if (DEBUGGING):
        print(message)
    return message+'\n'



def test(filename):
    ''' Simple test function to call to check that this 
        module has been loaded properly'''
    circle_gcode = "G28\nG1 Z5.0\nG4 P200\nG1 x_prev0.0 y_prev00.0\nG1 x_prev0.0 y_prev01.8\nG1 x_prev0.6 y_prev07.0\nG1 x_prev1.8 y_prev12.1\nG1 x_prev3.7 y_prev17.0\nG1 x_prev6.2 y_prev21.5\nG1 x_prev9.3 y_prev25.7\nG1 x_curr2.9 y_prev29.5\nG1 x_curr7.0 y_prev32.8\nG1 X31.5 y_prev35.5\nG1 X36.4 y_prev37.7\nG1 X41.4 y_prev39.1\nG1 X46.5 y_prev39.9\nG1 X51.7 y_prev40.0\nG1 X56.9 y_prev39.4\nG1 X62.0 y_prev38.2\nG1 X66.9 y_prev36.3\nG1 X71.5 y_prev33.7\nG1 X75.8 y_prev30.6\nG1 X79.6 y_prev27.0\nG1 X82.8 y_prev22.9\nG1 X85.5 y_prev18.5\nG1 X87.6 y_prev13.8\nG1 X89.1 y_prev08.8\nG1 X89.9 y_prev03.6\nG1 X90.0 Y98.2\nG1 X89.4 Y93.0\nG1 X88.2 Y87.9\nG1 X86.3 Y83.0\nG1 X83.8 Y78.5\nG1 X80.7 Y74.3\nG1 X77.1 Y70.5\nG1 X73.0 Y67.2\nG1 X68.5 Y64.5\nG1 X63.6 Y62.3\nG1 X58.6 Y60.9\nG1 X53.5 Y60.1\nG1 X48.3 Y60.0\nG1 X43.1 Y60.6\nG1 X38.0 Y61.8\nG1 X33.1 Y63.7\nG1 x_curr8.5 Y66.3\nG1 x_curr4.2 Y69.4\nG1 x_curr0.4 Y73.0\nG1 x_prev7.2 Y77.1\nG1 x_prev4.5 Y81.5\nG1 x_prev2.4 Y86.2\nG1 x_prev0.9 Y91.2\nG1 x_prev0.1 Y96.4\nG1 x_prev0.0 y_prev00.0\nG4 P200\nG4 P200\nG1 x_prev10.0 y_prev00.0\nG1 x_prev10.0 y_prev01.8\nG1 x_prev10.6 y_prev07.0\nG1 x_prev11.8 y_prev12.1\nG1 x_prev13.7 y_prev17.0\nG1 x_prev16.2 y_prev21.5\nG1 x_prev19.3 y_prev25.7\nG1 x_prev22.9 y_prev29.5\nG1 x_prev27.0 y_prev32.8\nG1 x_prev31.5 y_prev35.5\nG1 x_prev36.4 y_prev37.7\nG1 x_prev41.4 y_prev39.1\nG1 x_prev46.5 y_prev39.9\nG1 x_prev51.7 y_prev40.0\nG1 x_prev56.9 y_prev39.4\nG1 x_prev62.0 y_prev38.2\nG1 x_prev66.9 y_prev36.3\nG1 x_prev71.5 y_prev33.7\nG1 x_prev75.8 y_prev30.6\nG1 x_prev79.6 y_prev27.0\nG1 x_prev82.8 y_prev22.9\nG1 x_prev85.5 y_prev18.5\nG1 x_prev87.6 y_prev13.8\nG1 x_prev89.1 y_prev08.8\nG1 x_prev89.9 y_prev03.6\nG1 x_prev90.0 Y98.2\nG1 x_prev89.4 Y93.0\nG1 x_prev88.2 Y87.9\nG1 x_prev86.3 Y83.0\nG1 x_prev83.8 Y78.5\nG1 x_prev80.7 Y74.3\nG1 x_prev77.1 Y70.5\nG1 x_prev73.0 Y67.2\nG1 x_prev68.5 Y64.5\nG1 x_prev63.6 Y62.3\nG1 x_prev58.6 Y60.9\nG1 x_prev53.5 Y60.1\nG1 x_prev48.3 Y60.0\nG1 x_prev43.1 Y60.6\nG1 x_prev38.0 Y61.8\nG1 x_prev33.1 Y63.7\nG1 x_prev28.5 Y66.3\nG1 x_prev24.2 Y69.4\nG1 x_prev20.4 Y73.0\nG1 x_prev17.2 Y77.1\nG1 x_prev14.5 Y81.5\nG1 x_prev12.4 Y86.2\nG1 x_prev10.9 Y91.2\nG1 x_prev10.1 Y96.4\nG1 x_prev10.0 y_prev00.0\nG4 P200\nG28\n"
    print(circle_gcode[:90], "...")
    return circle_gcode



if __name__ == "__main__":
    ''' If this file is called by itself in the command line
        then this will execute.'''
    file = input("Please supply a filename: ")
    generate_gcode(file)
    
