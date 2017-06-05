"""
Visualization tool for creating a SVG of an OBJ textures's UV faces.
Written by Zachary Ferguson
"""

from __future__ import print_function, division
import os
import sys
import getopt
from recordclass import recordclass

import numpy

import includes

from obj_reader import load_obj


def save_lines(outFilename, lines):
    """
    Save out lines to the a file with the given outFilename. Appends a newline
    after each element of lines.
    """
    print("Saving:", outFilename)
    with open(outFilename, 'w') as out:
        for line in lines:
            print(line, file = out)


def generate_svg(mesh, width = 1024, height = 1024,
style="fill:#CC0000;stroke:#4D2828;stroke-width:0.5;stroke-linejoin:round",
colorClockwise = False):
    """
    Genererate the SVG lines for the given models UV faces.
    Inputs:
        mesh   - 3D model to generate UV faces. Should match the specifications
            of OBJ recordclass.
        width  - width of output SVG texture (Default: 1024)
        height - height of output SVG texture (Default: 1024)
        style  - Valid SVG style string for the style of the faces.
            (Default: "fill:#CC0000;stroke:#4D2828;stroke-width:0.5;
            stroke-linejoin:round")
        colorClockwise - Should clockwise faces be colored differently?
            (Default: False)
    Output:
        Returns a list of the lines for the SVG.
    """
    lines = []
    lines.append('<?xml version="1.0" encoding="utf-8"?>')
    lines.append('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" ' +
        '"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">')
    lines.append('<svg xmlns="http://www.w3.org/2000/svg" ' +
        'height = "%d" width = "%d">' % (width, height))
    lines.append(
        '<rect width="%d" height="%d" style="fill:black;stroke-width:0;"/>' %
        (width, height)
    )

    for face in mesh.f:
        vts = [mesh.vt[fv.vt] for fv in face]
        points = "".join(["%f,%f " % (uv.u * width, height - (uv.v * height))
            for uv in vts])

        tmp_style = style
        if(colorClockwise and len(face) == 3):
            # Create matrix as specified (http://goo.gl/BDPYIT)
            mat = numpy.array([[1, uv.u, uv.v] for uv in vts])
            if(numpy.linalg.det(mat) < 0): # If order is clockwise
                tmp_style = ("fill:#0000CC;stroke:#28284D;stroke-width:0.5;" +
                    "stroke-linejoin:round")

        lines.append('<polygon points = "%s" style = "%s" />' %
            (points, tmp_style))

    lines.append('</svg>')

    return lines


def insert_svg_comments(lineNum, lines, comments):
    """
        Inserts the strings in comments into lines at the lineNum position.
        Inserts the comments in svg comment syntax.
    """
    for comment in comments:
        lines.insert(lineNum, "<!-- %s -->" % comment)
        lineNum += 1


def insert_blank_line(lineNum, lines):
    """ Insert a blank line into the lines list. """
    lines.insert(lineNum, "")


if __name__ == '__main__':
    def usage(afterStr = ""):
        print('Usage:', sys.argv[0],
            'path/to/input.obj [-c] [-o path/to/output.svg] [-s svg_style]',
            file = sys.stderr)
        print(afterStr, file = sys.stderr)
        sys.exit(-1)

    if len(sys.argv) < 2:
        usage()

    argv = list(sys.argv[1:])

    inpath = argv.pop(0)
    outpath = os.path.splitext(inpath)[0] + '-visualize-uv.svg'
    styleStr = \
        "fill:#CC0000;stroke:#4D2828;stroke-width:0.5;stroke-linejoin:round"
    colorClockwise = False

    try:
        opts, argv = getopt.getopt(argv, "ho:s:c")
    except getopt.GetoptError as err:
        usage(err.msg)

    for opt, arg in opts:
        if(opt == "-h"):
            usage()
        elif(opt == "-o"):
            outpath = arg
        elif(opt == "-s"):
            styleStr = arg
        elif(opt == "-c"):
            colorClockwise = True

    mesh = load_obj(inpath)
    lines = generate_svg(mesh, style = styleStr,
        colorClockwise = colorClockwise)
    insert_svg_comments(2, lines,
        [os.path.split(outpath)[1], "Generated by %s" % sys.argv[0],
        "UV Faces for %s" % os.path.split(inpath)[1]])
    insert_blank_line(2, lines)
    insert_blank_line(6, lines)
    save_lines(outpath, lines)