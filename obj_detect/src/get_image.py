#!/usr/bin/env python3
import sys
#sys.path.insert(1, "/usr/local/lib/python3.5/dist-packages/cv2")
#sys.path.insert(0, '/opt/installer/open_cv/cv_bridge/lib/python3/dist-packages/')
sys.path.insert(0, '/opt/installer/open_cv/cv_bridge/lib/python3/dist-packages/')


import rospy
from std_msgs.msg import String
from sensor_msgs.msg import Image
from obj_detect.srv import obj_coordinate
# from get_image.srv import *
import datetime 
import cv2
import numpy as np
from cv_bridge import CvBridge, CvBridgeError
#from darknet.darknet import *
import darknet.darknet as darknet

import time 
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--Object_Name', type=str, default='.', help='Class name of training object.')
FLAGS = parser.parse_args()

day = str(datetime.datetime.now()).split(" ")[0]
time = str(datetime.datetime.now()).split(" ")[1]
time = time.split(":")[0] + "_" + time.split(":")[1] + "_" + time.split(":")[2].split(".")[0]

current_time = day + "_" + time + "_"

Object_Name = FLAGS.Object_Name

Train_Data_Dir = os.path.dirname(os.path.realpath(__file__)) + '/Training_Data/' + \
    current_time + '_' + Object_Name + '/'

value = None

###========== YOLOv4 config ==========###
win_title = 'YOLOv4 CUSTOM DETECTOR'
cfg_file = '/home/emol/ws_azure/src/obj_detect/src/darknet/data/yolov4-tiny-sam.cfg'
data_file = '/home/emol/ws_azure/src/obj_detect/src/darknet/data/sam.data'
weight_file = '/home/emol/ws_azure/src/obj_detect/src/darknet/data/weights/yolov4-tiny-sam_final.weights'

thre = 0.25
show_coordinates = True


network, class_names, class_colors = darknet.load_network(
        cfg_file,
        data_file,
        weight_file,
        batch_size=1
    )
  
width = darknet.network_width(network)
height = darknet.network_height(network)

class Get_image():
    def __init__(self):
        rospy.init_node('get_image_from_Azure', anonymous=True)

        self.obj_coor_x = 0
        self.obj_coor_y = 0
        
        self.bridge = CvBridge()
        self.image = np.zeros((0,0,3), np.uint8)
        self.depth_cv_image = np.zeros((0,0,1), np.uint8)
        self.take_picture_counter = 0
        self.take_depth_picture_counter = 0

        rospy.Subscriber("/rgb/image_raw", Image, self.callback)

        rospy.Service('obj_location', obj_coordinate, self.return_obj)

        # rospy.Subscriber("/camera/depth/image_rect_raw", Image, self.depth_callback)

        #self.pub = rospy.Publisher("object_coordinate", Coordinate_list, queue_size=10)

        #self.coor_list = Coordinate_list()


        if not os.path.exists(Train_Data_Dir):
            os.makedirs(Train_Data_Dir)
        
        rospy.spin()

    def return_obj(self, req):
            obj_x = self.obj_coor_x
            obj_y = self.obj_coor_y
            
            return (obj_x, obj_y)
      
    def depth_callback(self, depth_image):
        try:
            self.depth_cv_image = self.bridge.imgmsg_to_cv2(depth_image)
        except CvBridgeError as e:
            print(e)

        cv2.namedWindow("depth_result", cv2.WINDOW_NORMAL)
        cv2.imshow("result", self.depth_cv_image)
        self.get_image(self.depth_cv_image)
        cv2.waitKey(1)
    
    def callback(self, image):
        global value
        try:
            self.cv_image = self.bridge.imgmsg_to_cv2(image, "bgr8")

            frame_rgb = cv2.cvtColor( self.cv_image, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize( frame_rgb, (width, height))


            darknet_image = darknet.make_image(width, height, 3)
            darknet.copy_image_from_bytes(darknet_image, frame_resized.tobytes()) 


            detections = darknet.detect_image(network, class_names, darknet_image, thresh=thre)
            self.obj_coor_x, self.obj_coor_y = darknet.print_detections(detections, show_coordinates)

            #self.coor_list.x = int(obj_x)
            #self.coor_list.y = int(obj_y)

            #self.pub.publish(self.coor_list)

            darknet.free_image(darknet_image)
            image = darknet.draw_boxes(detections, frame_resized, class_colors)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        except CvBridgeError as e:
            print(e)
        
        cv2.namedWindow("result", cv2.WINDOW_NORMAL)
        cv2.imshow("result", image)   #image   #self.cv_image
        self.get_image(self.cv_image)
        cv2.waitKey(1)

    def get_image(self, crop_image):
        if cv2.waitKey(33) & 0xFF == ord('s'):
            name = str(Train_Data_Dir + current_time + '_' + Object_Name + '_' + str(self.take_picture_counter+1) + ".png")
            cv2.imwrite(name,crop_image)
            print("[Save] ", name)
            self.take_picture_counter += 1
        else:
            pass

    def get_depth_image(self, crop_image):
        if cv2.waitKey(33) & 0xFF == ord('d'):
            name = str(Train_Data_Dir + current_time + '_depth_' + Object_Name + '_' + str(self.take_picture_counter+1) + ".png")
            cv2.imwrite(name,crop_image)
            print("[Save] ", name)
            self.take_depth_picture_counter += 1
        else:
            pass


if __name__ == '__main__': 

    listener = Get_image()
    cv2.destroyAllWindows()
