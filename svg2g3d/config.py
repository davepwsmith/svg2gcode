#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Configuration file for SVG to GCODE converter
# For printing single layers with adhesive

# G-code prepended at the start of processing the SVG file
preamble = """;FLAVOR:RepRap
;TIME:37
G21 ;metric values
G90 ;absolute positioning
M302 ;run nozzle cold
M82 ;set extruder to absolute mode
M107 ;start with the fan off
G28 X0 Y0 ;move X/Y to min endstops
G28 Z0 ;move Z to min endstops
G1 Z15.0 F9000 ;move the platform down 15mm
G92 E0 ;zero the extruded length
G1 F200 E6 ;extrude 6 mm of feed stock
G92 E0 ;zero the extruded length again
G1 F9000
;Put printing message on LCD screen
M117 Printing...
;Generated with Cura_SteamEngine 2.1.2
;LAYER_COUNT:1
;LAYER:0
M107
G1 F1500.00 E-6.50000"""

#'''G-code emitted at the end of processing the SVG file'''
postamble = """M104 S0 ;extruder heater off
M140 S0 ;heated bed heater off (if you have it)
G91 ;relative positioning
G1 E-1 F300  ;retract the filament a bit before lifting the nozzle, to release some of the pressure
G1 Z+0.5 E-5 X-20 Y-20 F9000 ;move Z up a bit and retract filament even more
G28 X0 Y0 ;move X/Y to min endstops, so the head is out of the way
M84 ;steppers off
G90 ;absolute positioning
;End of Gcode"""

# G-code emitted before processing a SVG shape
shape_preamble = ""

# G-code emitted after processing a SVG shape
shape_postamble = ""

# A4 area:               210mm x 297mm
# Printer Cutting Area: ~178mm x ~344mm
# Testing Area:          150mm x 150mm  (for now)
# Print bed width in mm
bed_max_x = 200

# Print bed height in mm
bed_max_y = 200

# Feed Rate
feed_rate = 7200.00

# Extrusion Rate Multiplier
# Set the extrusion multiplier below where:
# [multiplier] = [G-Code E Value] / [Distance Traveled in Millimeters]
extrusion_multi = 12/10

#  Used to control the smoothness/sharpness of the curves.
#     Smaller the value greater the sharpness. Make sure the
#     value is greater than 0.1
smoothness = 0.2
