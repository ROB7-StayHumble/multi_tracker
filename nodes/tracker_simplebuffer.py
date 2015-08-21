#!/usr/bin/env python
from __future__ import division
import roslib
import rospy
import rosparam
import copy
import cv
import cv2
import numpy as np
import threading
import dynamic_reconfigure.server
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
from std_msgs.msg import Float32, Header, String

from multi_tracker.msg import Contourinfo, Contourlist
from multi_tracker.msg import Trackedobject, Trackedobjectlist
from multi_tracker.srv import resetBackgroundService

import image_processing

# for basler ace cameras, use camera_aravis
# https://github.com/ssafarik/camera_aravis
# rosrun camera_aravis camnode
# default image: /camera/image_raw

# for firefley cameras, camera1394 does not provide timestamps but otherwise works
# use point grey drivers
# http://wiki.ros.org/pointgrey_camera_driver
# rosrun pointgrey_camera_driver camera_node
# default image: /camera/image_mono

# Trajectory class to aid in drawing colored tracked trajectories with opencv
class Trajectory(object):
    def __init__(self, objid):
        self.objid = objid
        self.positions = []
        self.color = None
        self.covariances = []
        self.popout = 0

def draw_trajectory(img, pts, color, thickness):
    for i in range(len(pts)-3):
        try:
            cv2.line(img, (int(pts[i][0]), int(pts[i][1])), (int(pts[i+1][0]), int(pts[i+1][1])), color, thickness)
        except:
            pass
            print 'could not draw trajectory line, length pts: ', len(pts), 'i: ', i
            
# The main tracking class, a ROS node
class Tracker:
    def __init__(self):
        '''
        Default image_topic for:
            Basler ace cameras with camera_aravis driver: camera/image_raw
            Pt Grey Firefly cameras with pt grey driver : camera/image_mono
        '''
        # default parameters (parameter server overides them)
        self.params = { 'image_topic'       : '/camera/image_mono',
                        'threshold'         : 20,
                        'backgroundupdate'  : 0.001,
                        'camera_encoding'   : 'mono8', # fireflies are bgr8, basler gige cams are mono8
                        'min_persistence_to_draw'   : 10,
                        'max_frames_to_draw'        : 50,
                        'erode'                     : 1,
                        'dilate'                    : 2,
                        'max_change_in_frame'       : 0.2,
                        'min_size'                  : 5,
                        'max_size'                  : 200,
                        'liveview'                  : False,
                        'roi_l'                     : 0,
                        'roi_r'                     : -1,
                        'roi_b'                     : 0,
                        'roi_t'                     : -1,
                        }
        for parameter, value in self.params.items():
            try:
                p = '/multi_tracker/tracker/' + parameter
                self.params[parameter] = rospy.get_param(p)
            except:
                print 'Using default parameter: ', parameter, ' = ', value
                
        # initialize the node
        rospy.init_node('multi_tracker')
        self.nodename = rospy.get_name().rstrip('/')
        
        # background reset service
        self.reset_background_flag = False
        self.reset_background_service = rospy.Service("/multi_tracker/reset_background", resetBackgroundService, self.reset_background)
        
        # init cvbridge
        self.cvbridge = CvBridge()
        self.imgScaled      = None
        self.backgroundImage = None
        self.tracked_trajectories = {}
        
        # buffer locking
        self.lockBuffer = threading.Lock()
        self.image_buffer = []
        self.framestamp = None
        
        # Publishers - publish contours
        self.pubContours = rospy.Publisher('/multi_tracker/contours', Contourlist, queue_size=300)
        
        # Subscriptions - subscribe to images, and tracked objects
        sizeImage = 128+1024*1024*3 # Size of header + data.
        self.subImage = rospy.Subscriber(self.params['image_topic'], Image, self.image_callback, queue_size=60, buff_size=2*sizeImage, tcp_nodelay=True)

    def image_callback(self, rosimg):
        with self.lockBuffer:
            self.image_buffer.append(rosimg)

    def reset_background(self, service_call):
        self.reset_background_flag = True
        return 1
        
    def process_image_buffer(self, rosimg):
        if self.framestamp is not None:
            self.dtCamera = (rosimg.header.stamp - self.framestamp).to_sec()
        else:
            self.dtCamera = 0.03
        self.framenumber = rosimg.header.seq
        self.framestamp = rosimg.header.stamp
        
        # Convert the image.
        try:
            img = self.cvbridge.imgmsg_to_cv2(rosimg, 'passthrough') # might need to change to bgr for color cameras
        except CvBridgeError, e:
            rospy.logwarn ('Exception converting background image from ROS to opencv:  %s' % e)
            img = np.zeros((320,240))

        self.imgScaled = img
        self.shapeImage = self.imgScaled.shape # (height,width)
        
########### Call to image processing function ##############################################################
        self.process_image() # must be defined seperately - see "main" code at the bottom of this script
############################################################################################################
        
    def Main(self):
        while (not rospy.is_shutdown()):
            with self.lockBuffer:
                time_now = rospy.Time.now()
                if len(self.image_buffer) > 0:
                    self.process_image_buffer(self.image_buffer.pop(0))
                pt = (rospy.Time.now()-time_now).to_sec()
                if len(self.image_buffer) > 9:
                    rospy.logwarn("Tracking processing time exceeds acquisition rate. Processing time: %f, Buffer: %d", pt, len(self.image_buffer))
        cv2.destroyAllWindows()

#####################################################################################################
    
if __name__ == '__main__':
    
    image_processing_function = rospy.get_param('/multi_tracker/tracker/image_processor')
    image_processor = image_processing.__getattribute__(image_processing_function)
    Tracker.process_image = image_processor
    tracker = Tracker()
    tracker.Main()
