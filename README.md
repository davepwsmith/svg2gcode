# Python SVG to G-Code Converter
A fast svg to gcode compiler based on lightly modified code from github user [vishpat](https://github.com/vishpat)'s [svg2gcode repository](https://github.com/vishpat/svg2gcode).

The file `config.py` contains the configurations for the conversion (printer bed size, feed rate, extrusion rate multiplier etc).

Takes a folder of SVGs (selected with a file picker) and creates gcode for a single layer of paste extrusion.

## Installation
Simply clone this repo.
```
git clone https://github.com/davepwsmith/svg2gcode.git
```

## Usage
Run the script and pick a folder!

## Troubleshooting
Will fail if there are non-polygon coordinates in the SVG - check for stray anchors etc in illustrator

## Details
The compiler is based on the eggbot project and it basically converts all of the SVG shapes into bezier curves. The bezier curves are then recursively sub divided until desired smoothness is achieved. The sub curves are then approximated as lines which are then converted into g-code.
