#!/usr/bin/env python

"""
SVG Generator
@summary: Generates the SVG path and saves to disk

@author: Rob Hemsley
@contact: hello@robhemsley.co.uk
@copyright: Rob Hemsley 2013
"""

import os, sys

try:
    import config
except ImportError:
    print "Config Not Found"
    sys.exit(0)
    

class Scene:
    """
    Scene - Class
    @summary: The file to which the data will be saved - Think of this as the Canvas you draw upno
    """
    
    def __init__(self, name = "svg", width = 400, height = 400):
        """
        __init__ - Constructor
        @param name: The Name of the document
        @type name: String
        @param width: The width of the document - In what ever arbatory unit you wish (Look at the SVG spec it's mad)
        @type width: int
        @param height: The height of the document 
        """
        self.name   = name
        self.items  = []
        self.height = height
        self.width  = width

    def add(self, item):
        """
        add - Method
        @summary: Adds an SVG element to the document canvas
        @param item: The SVG element you wish to add
        @type item: List  
        """ 
        self.items.append(item)

    def strarray(self):
        """
        strarray - Method
        @summary: Poor mans sealize/pickle - Creates a list of the document XML SVG
        """
        var = ["<svg version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" xlink=\"http://www.w3.org/1999/xlink\" x=\"0px\" y=\"0px\" width=\"%fmm\" height=\"%fmm\" style=\"shape-rendering:geometricPrecision; text-rendering:geometricPrecision; image-rendering:optimizeQuality; fill-rule:evenodd; clip-rule:evenodd\" viewBox=\"0 0 %f %f\">\n" % (self.width, self.height, self.width, self.height),
               " <g style=\"fill-opacity:1.0; stroke:black;\n",
               "  stroke-width:1;\">\n"]
        #Construct the output string
        for item in self.items: 
            var += item.strarray()  
        #Close out the doc          
        var += [" </g>\n</svg>\n"]
        return var

    def write_svg(self, filename = None):
        """
        write_svg - Method
        @summary: Writes the svg document to the disk with the specified filename
        @param filename: The filename of the file to be created
        @type filename: String  
        """
        if filename:
            self.svgname = filename
        else:
            self.svgname = "%s%s"% (self.name, ".svg")
            
        file_out = open(self.svgname, 'w')
        file_out.writelines(self.strarray())
        file_out.close()

    def display(self, prog = config.SVG_DISPLAY_CMD):
        """
        display - method
        @summary: Opens the SVG file with the specified application
        @param prog: The program the SVG file should be opened with
        @type prog: String  
        """
        os.system("%s %s" % (prog, self.svgname))

class Line:
    """
    Line - Class
    @summary: Represents a line object in the SVG document
    """
    
    def __init__(self, start, end, colour, width):
        """
        __init__ - method
        @summary: Constructor for the line class
        @param start: The start co-ordinate
        @type start: Tuple
        @param end: The end co-ordinate
        @type end: Tuple
        @param colour: The colour of the line
        @type colour: Tuple
        @param width: The width of the line
        @type width: Int   
        """
        self.start  = start
        self.end    = end
        self.colour = colour
        self.width  = width

    def strarray(self):
        """
        strarray - Method
        @return: The XML string List for the SVG document
        @rtype: List
        """
        return ["  <line x1=\"%d\" y1=\"%d\" x2=\"%d\" y2=\"%d\" style=\"stroke:%s;stroke-width:%d\"/>\n" %\
                (self.start[0],self.start[1],self.end[0],self.end[1],colourstr(self.colour),self.width)]
        
class Polygon:
    """
    Polygon - Class
    @summary: Represents a Polygon object in the SVG document
    """
    
    def __init__(self, points, fill_colour, line_colour, line_width, other=""):
        """
        """
        self.points         = points
        self.fill_colour    = fill_colour
        self.line_colour    = line_colour
        self.line_width     = line_width
        self.other          = other
        
    def strarray(self):
        if type(self.fill_colour) != type("str"):
            self.fill_colour = colourstr(self.fill_colour)
        if type(self.fill_colour) != type("str"):
            self.line_colour = colourstr(self.line_colour)
            
        polygon="<polygon points=\""
        for point in self.points:
            polygon+=" %d,%d" % (point[0], point[1])
            
        return [polygon,\
               "\" \nstyle=\"fill:%s;stroke:%s;stroke-width:%f\" %s/>\n" %\
               (self.fill_colour, self.line_colour, self.line_width, self.other)]


class Text:
    """
    Text - Class
    @summary: 
    """
    
    def __init__(self, origin, text, size, colour):
        """
        __init__ - Method
        """
        self.origin     = origin
        self.text       = text
        self.size       = size
        self.colour     = colour

    def strarray(self):
        """
        strarray - method
        """
        return ["  <text style=\"letter-spacing:1;\" x=\"%d\" y=\"%d\" font-family=\"sans-serif\" font-size=\"%d\" fill=\"%s\">\n" %\
                (self.origin[0], self.origin[1], self.size, colourstr(self.colour)),
                "   %s\n" % self.text,
                "  </text>\n"]

def colourstr(rgb): 
    """
    colourstr - function
    """
    return "#%x%x%x" % (rgb[0]/16,rgb[1]/16,rgb[2]/16)

if __name__ == "__main__":
    scene = Scene("test")
    scene.add(Line((200,200), (200,300), (0,0,0), 1))
    scene.add(Line((200,200), (300,200), (0,0,0), 1))
    scene.add(Text((50,50), "Lovely Lovely Text", 24, (0,0,0)))
    scene.write_svg()
    scene.display()