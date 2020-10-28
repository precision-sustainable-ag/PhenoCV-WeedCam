# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 17:24:06 2020

@author: HP
"""
import argparse
import numpy as np
import cv2
import time
from PIL import Image
from tensorflow.lite.python.interpreter import Interpreter

# Deeplab color palettes
DEEPLAB_PALETTE = Image.open("colorpalette.png").getpalette()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--deep_model", default="3_class_model_mobilenet_v3_small_v2.1_1080x1920.tflite", help="Path of the deeplabv3plus model.")
    parser.add_argument('--image_width', type=int, default=1920, help='Model Image dimension (width). (Default=None)')
    parser.add_argument('--image_height', type=int, default=1080, help='Model Image dimension (height). (Default=None)')
    parser.add_argument("--num_threads", type=int, default=4, help="Threads.")
    args = parser.parse_args()

    deep_model    = args.deep_model
    image_width  = args.image_width
    image_height = args.image_height
    num_threads   = args.num_threads

    interpreter = Interpreter(model_path=deep_model)
    try:
        interpreter.set_num_threads(num_threads)
    except:
        print("WARNING: The installed PythonAPI of Tensorflow/Tensorflow Lite runtime does not support Multi-Thread processing.")
        print("WARNING: It works in single thread mode.")
        print("WARNING: If you want to use Multi-Thread to improve performance on aarch64/armv7l platforms, please refer to one of the below to implement a customized Tensorflow/Tensorflow Lite runtime.")
        print("https://github.com/PINTO0309/Tensorflow-bin.git")
        print("https://github.com/PINTO0309/TensorflowLite-bin.git")
        pass
    
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()[0]['index']
    deeplabv3_predictions = interpreter.get_output_details()[0]['index']

    color_image = cv2.imread("/home/pi/03_integer_quantization/soren_images/2020_10_02_10_58_15/color.png") # path to color image
    color_image = cv2.resize(color_image, (image_width, image_height)) 
    cv2.imshow("Input color image",color_image)

    
    prepimg_deep = cv2.resize(color_image, (image_width, image_height))
    prepimg_deep = cv2.cvtColor(prepimg_deep, cv2.COLOR_BGR2RGB)
    prepimg_deep = np.expand_dims(prepimg_deep, axis=0)
    prepimg_deep = prepimg_deep.astype(np.uint8)
        
    # Run model - DeeplabV3-plus
    start_time = time.time()
    interpreter.set_tensor(input_details, prepimg_deep)
    interpreter.invoke()

    # Get results
    predictions = interpreter.get_tensor(deeplabv3_predictions)[0]
    
    
    # Segmentation
    outputimg = np.uint8(predictions)
    outputimg = cv2.resize(outputimg, (image_width, image_height))
    outputimg = Image.fromarray(outputimg, mode="P")
    outputimg.putpalette(DEEPLAB_PALETTE)
    outputimg = outputimg.convert("RGB")
    outputimg = np.asarray(outputimg)
    outputimg = cv2.cvtColor(outputimg, cv2.COLOR_RGB2BGR)
    
    imdraw = cv2.addWeighted(color_image, 1.0, outputimg, 0.9, 0)
    print("--- %s seconds ---" % (time.time() - start_time))

    cv2.imshow("Segmented image", imdraw)
    cv2.imwrite("/home/pi/03_integer_quantization/soren_images/2020_10_02_10_58_15/segmentation.jpg", imdraw)
    cv2.imwrite("/home/pi/03_integer_quantization/soren_images/2020_10_02_10_58_15/mask image.jpg", outputimg)
    cv2.waitKey(0)&0xFF
