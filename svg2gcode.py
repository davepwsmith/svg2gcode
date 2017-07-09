#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from svg2g3d import generate_gcode
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()
svg_path = filedialog.askdirectory()

for file in os.listdir(os.path.abspath(svg_path)):
    if file.endswith(".svg"):
        path = os.path.abspath(svg_path)
        generate_gcode(path + "\\" + file)