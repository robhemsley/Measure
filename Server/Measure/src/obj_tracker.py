"""
Obj Tracker
@summary: Undertakes ORB pattern recognition on a passed image attempting to find a known target and it's homography.

@author: Rob Hemsley
@contact: hello@robhemsley.co.uk
@copyright: Rob Hemsley 2013
"""

#import base modules
import math, sys
from collections import namedtuple

#Import dependencies - cv2, numpy
try:
    import cv2
except ImportError:
    print "OpenCV Library Not Found - http://opencv.willowgarage.com/wiki/InstallGuide"
    sys.exit(0)
    
try:
    import numpy
except ImportError:
    print "Numpy Library Not Found - http://www.numpy.org"
    sys.exit(0)
    
import config
    

flann_params = dict(algorithm           = config.FLANN_INDEX_LSH,
                   table_number         = config.FLANN_TABLE_NUM,
                   key_size             = config.FLANN_KEY_SIZE,
                   multi_probe_level    = config.FLANN_MULTI_PROBE_LEVEL)

class ObjTarget:
    """
      image     - image to track
      rect      - tracked rectangle (x1, y1, x2, y2)
      keypoints - keypoints detected inside rect
      descrs    - their descriptors
      data      - some user-provided data
    """
    image       = None
    rect        = None
    keypoints   = None
    descrs      = None
    data        = None
    filename    = None
    side_length = None
    
    def __init__(self, image, rect, keypoints, descrs, data, filename, side_length):
        self.image          = image
        self.rect           = rect
        self.keypoints      = keypoints
        self.descrs         = descrs
        self.data           = data
        self.filename       = filename
        self.side_length    = side_length

class TrackedTarget:
    """
      target - reference to PlanarTarget
      p0     - matched points coords in target image
      p1     - matched points coords in input frame
      H      - homography matrix from p0 to p1
      quad   - target bounary quad in input frame
    """
    target  = None
    p0      = None
    p1      = None
    H       = None
    quad    = None
    
    def __init__(self, target, p0, p1, H, quad):
        self.target = target
        self.p0     = p0
        self.p1     = p1
        self.quad   = quad
        
    def getAvgLength(self):
        """
        getAvgLength - Method
        @summary: 
        @return: 
        @rtype: 
        """        
        avg_length = 0
        for i in range(4):
            if i == 3:
                second = 0
            else:
                second = i+1           
                 
            avg_length += math.sqrt((self.quad[second][0] - self.quad[i][0])**2 + (self.quad[second][1] - self.quad[i][1])**2 )

        
        #avg_length = (avg_length/4)
        if config.DEBUG:
            print "AVERAGE_LENGTH: Pixels", avg_length
        
        return avg_length

    def getPixPerMM(self):
        """
        getPixelPerMM - Method
        @summary: 
        @return: 
        @rtype: 
        """
        if config.DEBUG: print "PixPerMM: ", float(self.target.side_length/self.getAvgLength())
        return float(self.target.side_length/self.getAvgLength())
    
class ObjTracker:
    """
    ObjTracker - Class
    """
    
    def __init__(self):
        """
        __init__ - Method
        @summary: 
        """
        self.detector = cv2.ORB(nfeatures = 5000)
        self.matcher = cv2.FlannBasedMatcher(flann_params, {})  # bug : need to pass empty dict (#1329)
        self.targets = []

    def add_target(self, image, rect, data=None, filename=None, side_length=None):
        """
        add_target - Method
        @summary: 
        @param image:
        @type image: String
        
        @param rect:
        @type rect: Tuple
        
        @param data:
        @type param: 
        
        @param filename:
        @type filename: String
        
        @param side_length: 
        @type side_length: Int                
        """
        
        x0, y0, x1, y1 = rect
        
        image = cv2.imread(filename)
        raw_points, raw_descrs = self.detect_features(image)
        points, descs = [], []
        for kp, desc in zip(raw_points, raw_descrs):
            x, y = kp.pt
            if x0 <= x <= x1 and y0 <= y <= y1:
                points.append(kp)
                descs.append(desc)

        descs = numpy.uint8(descs)
        self.matcher.add([descs])
        target = ObjTarget(image = image, rect=rect, keypoints = points, descrs=descs, data=None, filename=filename, side_length=side_length)
        self.targets.append(target)

    def clear(self):
        """
        clear - Method
        @summary: Clears the local matcher and target trackers
        """
        self.targets = []
        self.matcher.clear()

    def track(self, frame):
        """
        track - Method
        @summary: Attempts to find the trackables within the passed frame
        """
        
        self.frame_points, self.frame_descrs = self.detect_features(frame)
        if len(self.frame_points) < config.FLANN_MIN_MATCH_COUNT:
            return []
        
        matches = self.matcher.knnMatch(self.frame_descrs, k = 2)
        matches = [m[0] for m in matches if len(m) == 2 and m[0].distance < m[1].distance * 0.75]
        if len(matches) < config.FLANN_MIN_MATCH_COUNT:
            return []
        
        matches_by_id = [[] for _ in xrange(len(self.targets))]
        for m in matches:
            matches_by_id[m.imgIdx].append(m)
            
        tracked = []
        for imgIdx, matches in enumerate(matches_by_id):
            if len(matches) < config.FLANN_MIN_MATCH_COUNT:
                continue
            
            target = self.targets[imgIdx]
            p0 = [target.keypoints[m.trainIdx].pt for m in matches]
            p1 = [self.frame_points[m.queryIdx].pt for m in matches]
            p0, p1 = numpy.float32((p0, p1))
            H, status = cv2.findHomography(p0, p1, cv2.RANSAC, 1.0)
            status = status.ravel() != 0

            if status.sum() < config.FLANN_MIN_MATCH_COUNT:
                continue
            
            p0, p1 = p0[status], p1[status]

            x0, y0, x1, y1 = target.rect
            quad = numpy.float32([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])
            quad = cv2.perspectiveTransform(quad.reshape(1, -1, 2), H).reshape(-1, 2)

            track = TrackedTarget(target = target, p0 = p0, p1 = p1, H = H, quad = quad)
            tracked.append(track)
            
        tracked.sort(key = lambda t: len(t.p0), reverse = True)
        
        return tracked

    def detect_features(self, frame):
        """
        detect_feature - Method
        @summary: Detects the feature keypoints within the frame and the frames descriptor
        @param frame:
        @type frame:  
        @return: keypoints, descriptors
        """

        keypoints, descrs = self.detector.detectAndCompute(frame, None)
        #If no descriptors found return None
        if descrs is None:
            descrs = []
            
        return keypoints, descrs

if __name__ == '__main__':
    print __doc__
