# -*- coding: utf-8 -*-
"""
Created on Sun Oct 18 22:27:55 2020

@author: sarde
"""
import numpy as np
import cv2 
import matplotlib.pyplot as plt
import tensorflow as tf
from PIL import Image
import imageio
import glob
import ntpath
import time
import os

import argparse
from pathlib import Path
from multiprocessing import Process
from time import time

from skimage.transform import resize
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=16)

parser = argparse.ArgumentParser()
parser.add_argument('-ip', '--input_path', \
    default='D:/00_NCSU/Fall2020/ECE633_IndividualTopics/OAK-D-Weed-Cam/Model/Images/', \
    type=str, help="Input Path")
parser.add_argument('-mp', '--model_path', \
    default = "D:/00_NCSU/Fall2020/ECE633_IndividualTopics/OAK-D-Weed-Cam/Model/deeplabv3+/models/3_class_model_mobilenet_v3_small_v1.0/3_class_model_mobilenet_v3_small_v1.0_513x513.pb", \
        type=str, help='Model Path')
parser.add_argument('-ms', '--model_size', default = 513, type=int, help='Model Input size')
args = parser.parse_args()

input_path = args.input_path
current_input_size=args.model_size
current_model = args.model_path

class DeepLabModel():
    """Class to load deeplab model and run inference."""

    INPUT_TENSOR_NAME = 'ImageTensor:0'
    OUTPUT_TENSOR_NAME = 'SemanticPredictions:0'
    SOFTMAX_TENSOR_NAME = 'SemanticProbabilities:0'
    INPUT_SIZE = current_input_size


    def __init__(self, path):
        """Creates and loads pretrained deeplab model."""
        self.graph = tf.Graph()

        graph_def = None
        # Extract frozen graph from tar archive.

        with tf.gfile.GFile(path, 'rb')as file_handle:
            graph_def = tf.GraphDef.FromString(file_handle.read())

        if graph_def is None:
            raise RuntimeError('Cannot find inference graph')

        with self.graph.as_default():
            tf.import_graph_def(graph_def, name='')
        
        # To Run on CPU, uncomment below and add config to self.session as: ", config=config"
        config = tf.ConfigProto(
            device_count = {'GPU': 0}
            )

        self.sess = tf.Session(graph=self.graph, config=config)


    def run(self, image):
        """Runs inference on a single image.

        Args:
          image: A PIL.Image object, raw input image.

        Returns:
          seg_map: np.array. values of pixels are classes
        """

        width, height,ch = image.shape

        resize_ratio = 1.0 * self.INPUT_SIZE / max(width, height)
        target_size = (int(resize_ratio * width), int(resize_ratio * height))

        resized_image = cv2.resize(image, (target_size))

        batch_seg_map, batch_prob_map = self.sess.run(
           [self.OUTPUT_TENSOR_NAME,
           self.SOFTMAX_TENSOR_NAME],
           feed_dict={self.INPUT_TENSOR_NAME: [np.asarray(image)]})

        seg_map = batch_seg_map[0]        
        # seg_map = resize(seg_map.astype(np.uint8), (height, width), preserve_range=True, order=0, anti_aliasing=False)
        prob_map = batch_prob_map[0]        
        return seg_map, prob_map
    
class CalcVolume:
    images=[]
    depths=[]    
    model = DeepLabModel(current_model)
    def __init__(self, input_path):
        for name in glob.glob(input_path+'*.png'):
            self.images.append(cv2.cvtColor(cv2.imread(name), cv2.COLOR_BGR2RGB))
        for name in glob.glob(input_path+'*.npy'):
            self.depths.append(np.load(name))
            
    def detect_white(self, image):
        hsv=cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        # define range of white color in HSV
        lower_white = np.array([0,0,0], dtype=np.uint8)
        upper_white = np.array([0,0,255], dtype=np.uint8)
        # Threshold the HSV image to get only white colors
        mask = cv2.inRange(hsv, lower_white, upper_white)
        # Bitwise-AND mask and original image
        res = cv2.bitwise_and(image,image, mask= mask)
        return mask, res
    
    def closing(self, rect):
        kernel = np.ones((5,5),np.uint8)
        dilation= cv2.dilate(rect, kernel, iterations = 35)
        closing = cv2.erode(dilation,kernel,iterations =32)
        return closing
    
    def floodFill(self,im_in):
        im_floodfill = im_in.copy()
        h, w = im_in.shape[:2]
        mask = np.zeros((h+2, w+2), np.uint8)
        # Floodfill from point (0, 0)
        cv2.floodFill(im_floodfill, mask, (0,0), (255,255,255));
        # Invert floodfilled image
        im_floodfill_inv = cv2.bitwise_not(im_floodfill)
        # Combine the two images to get the foreground.
        im_out = im_in | im_floodfill_inv    
        return im_floodfill, im_floodfill_inv, im_out
    
    def vis_depth(self,depth):
        depth=(65535//depth).astype(np.uint8)
        depth = cv2.applyColorMap(depth, cv2.COLORMAP_HOT)
        plt.imshow(depth)
    
    def calc_volume(self,mask_seg, area, depth_roi):
        vol=0
        non_zeros=np.where(mask_seg!=0)
        for i,j in zip(non_zeros[0], non_zeros[1]):
            vol+=(depth_roi[i][j]*0.001/np.count_nonzero(mask_seg))*area
        return vol

    def pipeline(self):
        for image, depth in zip(self.images, self.depths):
            plt.figure()
            plt.imshow(image)
            plt.figure()
            self.vis_depth(depth)
            print(image.shape)
            plt.imshow(image)
            _,mask=self.detect_white(image)
            plt.figure()
            plt.imshow(mask, cmap='gray')
            closing = self.closing(mask)
            plt.figure()
            plt.imshow(closing, cmap='gray')
            _, filled, _ = self.floodFill(closing)
            plt.figure()
            plt.imshow(filled, cmap='gray')            
            bin_mask=cv2.resize(cv2.cvtColor(filled, cv2.COLOR_RGB2GRAY), (1280, 720))
            plt.figure()
            plt.imshow(bin_mask, cmap='gray') 
            depth_roi=cv2.bitwise_and(depth, depth, mask=bin_mask)
            plt.figure()
            self.vis_depth(depth_roi)
            model_ip = cv2.resize(image, (current_input_size, current_input_size))
            seg_map, prob_map=self.model.run(model_ip)
            seg_mapr=cv2.resize(seg_map.astype(np.uint8),(depth.shape[1],depth.shape[0]), interpolation = cv2.INTER_LANCZOS4)
            print(seg_mapr.shape)
            plt.imshow(seg_mapr)
            mask_seg=cv2.bitwise_and(seg_mapr, seg_mapr, mask=bin_mask)
            plt.figure()
            plt.imshow(mask_seg)
            area = np.count_nonzero(mask_seg)/np.count_nonzero(bin_mask)*0.25
            vol=self.calc_volume(mask_seg,area, depth_roi)
            print(vol)

    
if __name__ == "__main__":
    calc_vol=CalcVolume(input_path)
    calc_vol.pipeline()
    
    