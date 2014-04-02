#/usr/bin/env python

"""
Measure
Provides wrapper functionality for the detection and measurement of an object. 
Can be used as a stand-alone module without the web server.

@author: Rob Hemsley
@contact: hello@robhemsley.co.uk
@copyright: Rob Hemsley 2013
"""

#Import standard modules
import math, time, os, random, sys

#Import dependencies - cv2, SimpleCV, PIL, numpy
try:
    import cv2
except ImportError:
    print "OpenCV Library Not Found - http://opencv.willowgarage.com/wiki/InstallGuide"
    sys.exit(0)
    
try:
    import SimpleCV
except ImportError:
    print "SimpleCV Not Found - http://simplecv.org"
    sys.exit(0)
    
try:
    import ImageDraw, Image, ImageFont
except ImportError:
    print "Python Imaging Library Not Found - http://www.pythonware.com/products/pil/"
    sys.exit(0)
    
try:
    import numpy
except ImportError:
    print "Numpy Library Not Found - http://www.numpy.org"
    sys.exit(0)

#Import required local modules
import obj_tracker              #Provides 'markerless' tracking
import config                   #Holds global varaiables
import svg                      #Generates the SVG file



class Target:
    """
    Target - Class
    @summary: Represents the tracked object within the scene
    """
    filename        = ""
    side_length     = 50
    rect            = ()
    
    def __init__(self, filename, rect, side_length = 50):
        """
        __init__ - Constructor
        
        @param filename: String containing the full path name
        @param rect: Tuple containing the coordinates for the location of the tag within the image
        @param side_length: The length of a side of the target tag (mm)   
        """
        self.filename = filename
        self.rect = rect
        self.side_length = side_length

        self.width = abs(rect[0]-rect[2])
        self.height = abs(rect[1]-rect[3])

class Material:
    """
    Material - Class
    @summary: Represents a detected material with the dimensions for the interior and exterior  
    """
    interior    = None
    exterior    = None
    _contours   = None
    pixpermm    = None
    filename    = None
    tag         = None
    img         = None
    scale       = 0


    def __init__(self, contours, image, tag = None, filename = None):
        """
        __init__ - Constructor
        
        @param contours:
        @param image:
        @param tag:
        @param filename:    
        """
        self._contours = contours
        self.pixpermm = tag.getPixPerMM()
        if self.pixpermm != None:
            self.scale = float(1)-(float(self.pixpermm)/10)
            
        self.interior = []
        self.tag = tag
        self.img = image
        self._findExterior()
        self._findInterior()
        self.filename = filename
                    
    def _findExterior(self):
        """
        _findExterior - Method
        @summary: Loops over the internal contours and finds the largest continuous contour
        which we use as the exterior for the material.
        """
        max_area = 0
        max_cnt = None
        
        for cnt in self._contours:
            area = cv2.contourArea(cnt)
            x, y, w, h = cv2.boundingRect(cnt)
            if len(cnt) >= 4 and area > 10:
                rect = cv2.minAreaRect(cnt)
                tmp = (w*h)
                
                #Sometimes it detects the outline of the entire image                
                for points in numpy.int0(cv2.cv.BoxPoints(rect)):
                    if points[0] < 2:
                        if config.DEBUG:
                            print "Found Outline of Window- Opps"
                        tmp = 0
                        break
                
                if tmp >= max_area:
                    max_area = tmp
                    max_cnt = cnt
                   
        self.exterior = max_cnt
    
    def _findInterior(self):
        """
        _findInterior - Method
        @summary: Loops over the internal contours and finds all appropriate outlines of the shape 
        """
        if self.exterior == None:
            self._findExterior()
                
        for cnt in self._contours:
            area = cv2.contourArea(cnt)
            #Try to prune out shapes without enough points or area
            if len(cnt) > 4 and area > 40:                
                x, y, w, h = cv2.boundingRect(cnt)            
                bb_x, bb_y, bb_w, bb_h = cv2.boundingRect(self.exterior)

                #Check that this isn't the ruler thats been detected
                if x > bb_x and y > bb_y and (x+w) < (bb_x+bb_w) and (y+h) < (bb_y+bb_h):
                    check_1 = cv2.pointPolygonTest(numpy.int32([numpy.int32(self.tag.quad)]), (x,y), True)
                    check_2 = cv2.pointPolygonTest(numpy.int32([numpy.int32(self.tag.quad)]), (x+w,y+h), True)

                    if check_1 < 0 and check_2 < 0:
                        self.interior.append(cnt)    
    
    def _calBBArea(self, bb):
        """
        _calBBArea - Method
        @summary: Calculates the area of a bounding box
        @return: Area of the bounding box
        @rtype: int
        """
        x_delta =  abs(bb[1][0] - bb[0][0])
        y_delta = abs(bb[1][1] - bb[0][1])
        box_area = x_delta * y_delta
        return box_area
    
    def getBoundingBox(self):
        """
        getBoundingBox - Method
        @summary: Returns the bounding box for the exterior of the material
        @return: The bounding box for the shape
        @rtype: tuple
        """
        rect = cv2.minAreaRect(self.exterior)
        box = cv2.cv.BoxPoints(rect)
        
        return box
    
    def getArea(self):
        """
        getArea - Method
        @summary: Returns the area of the material (exterior - interior)
        @todo: At the moment it divides the interior by 2 as it seems to detect multiple paths.
        This needs to be filtered better
        """
        interior = 0
        for x in self.interior:
            interior += self._getArea(x)
        interior = interior/2
            
        return self._getArea(self.exterior)-interior
        
    def getHeight(self):
        """
        getHeight - Method
        @summary: Returns the height of the objects BB
        @return: Height im mm of bb
        @rtype: int
        """
        w, h = self._getWidthHeight(self.exterior)

        if h > w:
            return w*self.pixpermm
        else:
            return h*self.pixpermm
   
    def getWidth(self):
        """
        getHWidth - Method
        @summary: Returns the width of the objects BB
        @return: Width im mm of bb
        @rtype: int
        """
        w, h = self._getWidthHeight(self.exterior)
        
        if h > w:
            return h*self.pixpermm
        else:
            return w*self.pixpermm
        
    def _getWidthHeight(self, contour):
        """
        _getWidthHeight - Method
        @summary: Returns the height and width of the BB in pixels
        @param contour: 
        @type contour:  
        @return: Height, Width of the BB in pixels
        @rtype: int
        """
        rect = cv2.minAreaRect(contour)
        box = cv2.cv.BoxPoints(rect)
        box = numpy.int0(box)
        
        w_1 = math.sqrt((box[1][0] - box[0][0])**2 + (box[1][1] - box[0][1])**2 )
        w_2 = math.sqrt((box[3][0] - box[2][0])**2 + (box[3][1] - box[2][1])**2 )

        w = (w_1+w_2)/2
        
        h_1 = math.sqrt((box[2][0] - box[1][0])**2 + (box[2][1] - box[1][1])**2 )
        h_2 = math.sqrt((box[0][0] - box[3][0])**2 + (box[0][1] - box[3][1])**2 )

        h = (h_1+h_2)/2
        
        return (w,h)
        
    def _getArea(self, contour):
        """
        _getArea - Method
        @summary: Returns the area of a contour in mm squared
        @param contour: 
        @type contour:  
        @return: The area of the contour
        @rtype: int
        """
        w, h = self._getWidthHeight(contour)
        return (w*self.pixpermm)*(h*self.pixpermm)
    
    def getStats(self, add_contours = False):
        """
        getStats - Method
        @summary: Returns stats for the material
        @param add_contours: Indicate if contours should be included
        @type add_contours: Boolean  
        @return: Dictionary of the stats
        @rtype: Dict
        """
        output = []
        for i in self.interior:
            output.append(self._genStats(i, add_contours))
            
        return {"exterior": self._genStats(self.exterior), "interior": output}
    
    def getCentrePoint(self):
        """
        getCentrePoint - Method
        @summary: Returns the coordinates for the center of the material BB (Used for rotation)
        @return: Coordinate for the centre of the object
        @rtype: Tuple
        """
        rect = cv2.minAreaRect(self.exterior)
        box = cv2.cv.BoxPoints(rect)
        box = numpy.int0(box)
        
        min_x = 10000000
        max_x = 0
        min_y = 10000000
        max_y = 0
        for loc in box:
            if loc[0] > max_x:
                max_x = loc[0]
                
            if loc[0] < min_x:
                min_x = loc[0]
                
            if loc[1] > max_y:
                max_y = loc[1]
                
            if loc[1] < min_x:
                min_y = loc[1]
                
        x = (max_x - min_x)/2
        y = (max_y - min_y)/2
        
        return (min_x+x, min_y+y)
    
    def _genStats(self, contour, add_contours = False):
        """
        _getStats - Method
        @summary: Generates statistics for contours
        @param contour: 
        @type contour:  
        @param add_contours: Add contours to dict
        @type add_contours: Boolean  
        @return: Statistics for the passed contours
        @rtype: Dict
        """
        h, w = self._getWidthHeight(contour)
        area = self._getArea(contour)
        
        rect = cv2.minAreaRect(contour)
        box = cv2.cv.BoxPoints(rect)
        min_box = numpy.int0(box)
        
        boundRect = cv2.boundingRect(self.exterior)
        
        if add_contours:
            return {"height": round(h), "width": round(w), "bound_rect": boundRect, "min__bound_box": min_box, "area":area, "points": contour}
        else:
            return {"holes": str(len(self.interior)),"_timestamp": str(time.time()),"height": str(round(h*self.pixpermm)), "width": str(round(w*self.pixpermm)), "_bound_rect": boundRect, "area":str(round(area)), "_svg": "http://%s/svg/%s"% (config.SERVER, os.path.basename(self.filename)[:os.path.basename(self.filename).index(".")]+".svg"), "_outline": "http://%s/outline/%s"% (config.SERVER, os.path.basename(self.filename))}
    
    def draw(self):
        """
        draw - Method
        @summary: 
        """
        #Internal shape colour - Blue
        colours = [(89, 73, 48)]
        
        for x in self.interior:
            cv2.drawContours(self.img, [x], 0, colours[random.randint(0, len(colours)-1)],2)
        
        cv2.drawContours(self.img, [self.exterior], 0, (43, 58, 255),2)      
        rect = cv2.minAreaRect(self.exterior)
        box = cv2.cv.BoxPoints(rect)
        box = numpy.int0(box)
        
        if config.DEBUG:
            #Draw the center point 
            cv2.circle(self.img, self.getCentrePoint(), 10, (0,0,255))    
            cv2.drawContours(self.img, [box],0,(0,0,255),2)
            cv2.imshow('Material', self.img)
            
        img1 = Image.fromarray(cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB))
        
        self._drawLine(img1, [(box[0][0], box[0][1]), (box[1][0], box[1][1])], (255, 58, 48))
        self._drawLine(img1, [(box[1][0], box[1][1]), (box[2][0], box[2][1])], (255, 58, 48))
        self._drawLine(img1, [(box[2][0], box[2][1]), (box[3][0], box[3][1])], (255, 58, 48))
        self._drawLine(img1, [(box[3][0], box[3][1]), (box[0][0], box[0][1])], (255, 58, 48))
        
        for x in self.interior:
            rect = cv2.minAreaRect(x)
            box = cv2.cv.BoxPoints(rect)
            box = numpy.int0(box)
            
            self._drawLine(img1, [(box[0][0], box[0][1]), (box[1][0], box[1][1])], (48, 73, 89))
            self._drawLine(img1, [(box[1][0], box[1][1]), (box[2][0], box[2][1])], (48, 73, 89))
            self._drawLine(img1, [(box[2][0], box[2][1]), (box[3][0], box[3][1])], (48, 73, 89))
            self._drawLine(img1, [(box[3][0], box[3][1]), (box[0][0], box[0][1])], (48, 73, 89))

        quad = self.tag.quad
        self._drawLine(img1, [(quad[0][0], quad[0][1]), (quad[1][0], quad[1][1])], (96, 96, 96), 2, False)
        self._drawLine(img1, [(quad[1][0], quad[1][1]), (quad[2][0], quad[2][1])], (96, 96, 96), 2, False)
        self._drawLine(img1, [(quad[2][0], quad[2][1]), (quad[3][0], quad[3][1])], (96, 96, 96), 2, False)
        self._drawLine(img1, [(quad[3][0], quad[3][1]), (quad[0][0], quad[0][1])], (96, 96, 96), 2, False)
        
            
        if config.DEBUG:
            img1.show()
            
        img1.save(os.path.abspath(config.OUTLINE_DIR+os.path.basename(self.filename)), "JPEG")
        
    def _drawLine(self, img, coords, colour, widthin = 1, draw_txt = True):
        """
        _drawLine - Method
        @summary: Generates the outline image with dimensions
        @param img: Image 
        @type img:  
        @param coords: The coordinates to draw
        @type coords:
        @param colour: The colour to draw the outline
        @type colour: Tuple    
        """
        draw = ImageDraw.Draw(img)
        draw.line(coords, fill = colour, width = widthin)
        font = ImageFont.truetype(
            'res/Gotham Light.TTF', 20
        )
        
        if coords[1][0] > coords[0][0]:
            x_offset = coords[0][0]
        else:
            x_offset = coords[1][0]
            
        if coords[1][1] > coords[0][1]:
            y_offset = coords[0][1]
        else:
            y_offset = coords[1][1]
            
        middle_x = x_offset + abs(coords[0][0] - coords[1][0])/2
        middle_y = y_offset + abs(coords[0][1] - coords[1][1])/2
        
        dist = str(round(math.sqrt((coords[1][0] - coords[0][0])**2 + (coords[1][1] - coords[0][1])**2 )*self.pixpermm))
        if draw_txt:
            draw.text((middle_x-20, middle_y), dist+" mm", font=font)
        del draw 
        
    def createSvg(self):
        """
        createSvg - Method
        @summary: Generates the SVG file for the material
        @return: The SVG Scene Canvas Element
        @rtype: Scene (See SVG module)
        """
        h, w = self.img.shape[:2]
        
        bb_x, bb_y, bb_w, bb_h = cv2.boundingRect(self.exterior)
        
        scene = svg.Scene(config.SVG_DOC_NAME, height= h*2, width= w*2)
        scene.add(svg.Text((5,10),"Height %dmm, Width %dmm"%(self.getHeight(), self.getWidth()), 5,(0,0,0)))
            
        rect = cv2.minAreaRect(self.exterior)
        box = cv2.cv.BoxPoints(rect)
        box = numpy.int0(box)
        
        min_x = 10000000
        max_x = -1
        min_y = 10000000
        max_y = -1
        
        min_x_loc = None
        min_y_loc = None
        
        for loc in box:
            print "loc,",loc
            if loc[0] >= max_x:
                max_x = loc[0]
                
            if loc[0] <= min_x:
                min_x = loc[0]
                min_x_loc = loc
                
            if loc[1] >= max_y:
                max_y = loc[1]
                
            if loc[1] <= min_y:
                min_y = loc[1]
                min_y_loc = loc
            
        x = (max_x - min_x)/2
        y = (max_y - min_y)/2
        
        if min_x_loc[0] > min_y_loc[0]:
            p1 = min_y_loc
            p2 = min_x_loc
        else:
            p1 = min_x_loc
            p2 = min_y_loc  
        
        deltaY = p2[1] - p1[1]
        deltaX = p2[0] - p1[0]
        
        coord = []
        for cnt in self.exterior:
            coord.append([cnt[0][0]-bb_x,cnt[0][1]-bb_y])

        angleInDegrees = abs(math.atan2(deltaY, deltaX) * 180 / math.pi)
        
        cv2.circle(self.img, (min_x+x,min_y+y), 10, (0,0,255))
        
        scene.add(svg.Polygon(coord, "none", "red", 0.0762, "transform=\"translate(%d, %d) rotate(%d %d %d) scale(%s) \""%(0, 0, angleInDegrees, p1[0], p1[1], self.scale)))
        for all_cnt in self.interior:
            coord = []
            for cnt in all_cnt:
                coord.append([cnt[0][0]-bb_x, cnt[0][1]-bb_y])

            scene.add(svg.Polygon(coord, "none", "blue", 0.0762, "transform=\"translate(%d, %d) rotate(%d %d %d) scale(%s)\""%(0, 0, angleInDegrees, p1[0], p1[1], self.scale)))
        
        return scene
        

class Measure:
    """
    Measure - Class
    @summary: The main application for processing the image
    """
    _tracker = obj_tracker.ObjTracker()
    
    def add_target(self, target):
        """
        add_target - Method
        @summary: Adds a tag to be tracked within the image
        @param target: The target object to add to the applicaiton
        @type target: Target (obj_tracker.py)  
        """
        self._tracker.add_target(cv2.imread(target.filename), target.rect, filename=target.filename, side_length=target.side_length)
        
        if config.DEBUG:
            target_id = len(self._tracker.targets)-1
            track_marker = self._tracker.targets[target_id].image.copy()
            for kp in self._tracker.targets[target_id].keypoints:
                x = int(kp.pt[0])
                y = int(kp.pt[1])
                cv2.circle(track_marker, (x, y), 2, (255, 0, 0))

            cv2.imshow('Tracked_Marker_%d'% (target_id), track_marker)
        
    
    def process(self, img):
        """
        process - Method
        @summary: Processes the passed image
        @param img: The filename of the image to be processed
        @type param: String
        @return: Material object if processing successeds
        @rtype: Material/None
        """
        img_colour = cv2.imread(img)
        
        hmm = img_colour.copy()
        tags = self.detect_tags(img_colour)
        
        if len(tags) < 1:
            print "NO TAG FOUND"
            return None
        
        else:
            tag = tags[0]
            contours = self.detect_shape(img, tag)
            material = Material(contours, hmm, tag, img)
            
            if config.DEBUG: material.draw()    
            
            return material
        
    def detect_shape(self, img, tag):
        """
        detect_shape - method
        @summary: Detects the contours for the images which are used from drawing
        @param img: The image to be processed
        @type img: String
        @param tag: The Tag object being tracked
        @return: The contours from the processed image
        @rtype: List Numpy values
        """
        img1 = SimpleCV.Image(img)
        img1 = img1.smooth()
            
        tag_x, tag_y, tag_w, tag_h = cv2.boundingRect(numpy.int32([numpy.int32(tag.quad)]))
            
        if config.DEBUG:
            rect = cv2.minAreaRect(numpy.int32([numpy.int32(tag.quad)]))
            box = cv2.cv.BoxPoints(rect)
            box = numpy.int0(box)
            debug_img = cv2.imread(img)
            cv2.drawContours(debug_img, [box], 0, (0, 255, 0),2) 
            cv2.imshow("Colour Image (1)", debug_img)
            
        img_sample = cv2.imread(img)
        out = []
        out.append(cv2.cv.Get2D(cv2.cv.fromarray(img_sample), tag_y-10, tag_x-10))
        out.append(cv2.cv.Get2D(cv2.cv.fromarray(img_sample), tag_y-10, (tag_x+tag_w)+10))
        out.append(cv2.cv.Get2D(cv2.cv.fromarray(img_sample), tag_y+tag_h+10, tag_x-10))
        out.append(cv2.cv.Get2D(cv2.cv.fromarray(img_sample), tag_y+tag_h+10, tag_x+tag_w+10))
            
        rgb = [0, 0, 0]
        for colour in out:
            rgb[0] += colour[2]
            rgb[1] += colour[1]
            rgb[2] += colour[0]
            
        rgb[0] = rgb[0]/4
        rgb[1] = rgb[1]/4
        rgb[2] = rgb[2]/4
        if config.DEBUG: print "Mean Colour:",str(rgb)        
        
        hue_distance = img1.smooth('gaussian')
        hue_distance = hue_distance.morphClose()
        
        pre_img = hue_distance.binarizeCv2(-1, 255, 0, 5);

        if config.DEBUG: 
            blobs = img1.findBlobs(minsize=50)
            blobs.draw(width=3, color=(235, 22, 8))
            img1.show()
                
        canny_gray = cv2.Canny(numpy.array(cv2.cv.GetMat(pre_img)), 20, 200)
        if config.DEBUG: cv2.imshow('Canny Image (8)', canny_gray)
            
        contours, hierarchy = cv2.findContours(numpy.array(cv2.cv.GetMat(pre_img)), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        debug_img1 = cv2.imread(img)
        cv2.drawContours(debug_img1, contours, -1, (0, 255, 0), 2) 
        if config.DEBUG: cv2.imshow('All Contours', debug_img1)
        
        return contours

    def detect_tags(self, img):
        """
        detect_tags - method
        @summary: Detects the tag within the image
        @param img: The image ot be processed
        @type img: String
        @return: The object discovered within the image 
        @rtype: List
        """
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        tracked = self._tracker.track(gray_img)
        
        if config.DEBUG: 
            debug_img = img.copy()
            frame_points, frame_descrs = self._tracker.detect_features(gray_img)
            for kp in frame_points:
                x = int(kp.pt[0])
                y = int(kp.pt[1])
                cv2.circle(debug_img, (x, y), 2, (255, 0, 0))  
                
            cv2.imshow("ORB Keypoints", debug_img)
        
        if len(tracked) > 0:
            if config.DEBUG:
                for id, target in enumerate(tracked):
                    cv2.polylines(img, [numpy.int32(target.quad)], True, (255, 255, 255), 2)        
            
                    for (x0, y0), (x1, y1) in zip(numpy.int32(target.p0), numpy.int32(target.p1)):  
                        cv2.circle(img, (x1, y1), 2, (255, 0, 0))
                    cv2.imshow("Homography_%d"%(id), img)
        
            return tracked
                
        return []


if __name__ == '__main__':
    measure = Measure()
    
    #New Ruler Graphics
    measure.add_target(Target("test_files/TargetRuler.jpg", (218, 402, 474, 488), 99))    
    material = measure.process("test_files/MaterialRuler.jpg")

    #Older Ruler File
    #measure.add_target(Target("test_files/TargetSqaure.jpg", (218, 402, 356, 546), 99))    
    #material = measure.process("test_files/MaterialSquare.jpg")#templates/material.jpg")
    
    out = ""
    if material != None:
        print "DEBUG STATS: \n", material.getStats(False)
        svg_file = material.createSvg()
        
        for line in svg_file.strarray():
            out += line 
            
        print "SVG DATA: \n", out
    
    if config.DEBUG:
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    