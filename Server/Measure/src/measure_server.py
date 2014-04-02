#!/usr/bin/env python

"""
measure_server

The main module for the measure app. Takes an input image and computes the outline, SVG and stats 

@author: Rob Hemsley
@contact: hello@robhemsley.co.uk
@copyright: Rob Hemsley 2013
"""

#Standard imports
import os.path, uuid, json, sys

#Import dependencies - tornado web servicer
try:
    import tornado.ioloop
    import tornado.options
    import tornado.web
    from tornado.options import define
except ImportError:
    print "Tornado Library Not Found - http://lmgtfy.com/?search=Python%20Tornado"
    sys.exit(0)

#Import dependencies - associated measure modules
try:
    import measure, config
except ImportError:
    print "Wow you broke it... Can't find config or measure - Probably copied or moved dirs"
    sys.exit(0)

define("port", default = 9000, help = "run on the given port", type = int)

#Create global ref to the measure library
measureControl = measure.Measure()

#Load Single Tag From the targets directory - Coordinates of the tag within the image are needed
#add_target(<Target>, (<rect_point1_x>, <rect_point1_y>, <rect_point2_x>, <rect_point2_y>), <size_mm>)

#measureControl.add_target(measure.Target(os.path.abspath("targets/TargetRuler.jpg"), (218, 402, 356, 546), 100))        
measureControl.add_target(measure.Target(os.path.abspath("targets/TargetQuarter.jpg"), (100, 100, 404, 399), 100))    
measureControl.add_target(measure.Target(os.path.abspath("targets/Target10Dollar.jpg"), (100, 100, 320, 320), 264))    
measureControl.add_target(measure.Target(os.path.abspath("targets/TargetIDMITRect.jpg"), (100, 100, 572, 400), 278))    

    
class MeasureApplication(tornado.web.Application):
    """
    Application - Class
    @summary: The main application handler for measure. ie. Routes traffic based on domain
    """
    
    def __init__(self):
        handlers = [
            (r"/", FlowAppHandler),                 #Root
            (r"/measure", MeasureHandler),          #Upload image to service
            (r"/outline/(.*?)", OutlineHandler),    #Outline JPG
            (r"/svg/(.*?)", SvgHandler),            #Outline SVG
        ]
        
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies = False,
            autoescape = None,
            xheaders = True,
            debug = config.DEBUG
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class FlowAppHandler(tornado.web.RequestHandler):
    """
    FlowAppHandler - Class
    @summary: Handler for the root of the app. Shows the basic web based upload image service 
    """
    
    def get(self):
        """
        get - Method
        @summary: Handler for HTTP get
        """
        self.render("measure_index.html")
        
class OutlineHandler(tornado.web.RequestHandler):
    """
    OutlineHandler - Class
    @summary: Handler for returning the outline of the image
    """
    
    def get(self, id_filename):
        """
        get - Method
        @summary: Returns the Outline image from the local system
        """
        self.set_header("Content-Type", "image/jpeg")

        File = open(os.path.abspath(config.OUTLINE_DIR+id_filename), "r")
        self.write(File.read())
        File.close()
        
class SvgHandler(tornado.web.RequestHandler):
    """
    SvgHandler - Class
    @summary: Handler for returning the SVG image
    """
    
    def get(self, id_filename):
        """
        get - Method
        @summary: Returns the SVG image for the material
        @param id_filename: The name of the file which will be loaded
        @type id_filename: Sting  
        """
        self.set_header("Content-Type", "image/svg+xml")

        File = open(os.path.abspath(config.SVG_DIR+id_filename),"r")
        self.write(File.read())
        File.close()

class MeasureHandler(tornado.web.RequestHandler):
    """
    MeasureHandler - Class
    @summary: main handler for processing passed images to the service
    """

    def post(self):
        """
        post - Method
        @summary: Called when an image is posted to the service
        """
        if config.DEBUG: print "Measure Post"

        #Get the posted Image        
        measure_image = self.request.files['measure_img'][0]
        tmp, ext =  os.path.splitext(measure_image["filename"])
        path = ""
        
        #Gen a uuid for the image
        while True:
            uuid_str = str(uuid.uuid4())
            path = str(os.path.abspath(config.SCANS_DIR+uuid_str+ext))
            if os.path.exists(path) == False:
                break
    
        output_file = open(path, 'w')
        output_file.write(measure_image['body'])
        output_file.close()
        
        print path
                
        #Measure the material image    
        material = measureControl.process(path)
        
        out = {}
        if material != None:
            material.draw()

            out = material.getStats() 
            svg = material.createSvg()
            svg.write_svg(os.path.abspath("%s%s.svg"% (config.SVG_DIR, uuid_str)))
    
            print "SVG Data", out
        
        else:
            #Return 
            out = {"ERROR": "1", "ERROR_MSG": config.ERROR_NO_RULER}
            
        self.finish(json.dumps(out))
        
if __name__ == "__main__":
    tornado.options.parse_command_line()
    measureApp = MeasureApplication()
    
    measureApp.listen(config.PORT)
    tornado.ioloop.IOLoop.instance().start()