import tensorflow as tf
import numpy as np
from PIL import Image
import imageio
import glob
import ntpath
import time
import os

from skimage.transform import resize
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=16)
futures = []

# The model is currently frozen with a max input resolution of 2048x2048 pixel. Images will automatically be resized to this before inference
current_input_size = 2048
im_input_path = "../images/"
im_output_path = "output/"
current_model = "3_class_model_v1.2/3_class_model_v1.2.pb"

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
        #config = tf.ConfigProto(
        #    device_count = {'GPU': 0}
        #    )

        self.sess = tf.Session(graph=self.graph)


    def run(self, image):
        """Runs inference on a single image.

        Args:
          image: A PIL.Image object, raw input image.

        Returns:
          seg_map: np.array. values of pixels are classes
        """

        #width, height = image.size

        #resize_ratio = 1.0 * self.INPUT_SIZE / max(width, height)
        #target_size = (int(resize_ratio * width), int(resize_ratio * height))

        #resized_image = image.convert('RGB').resize(target_size, Image.ANTIALIAS)

        batch_seg_map, batch_prob_map = self.sess.run(
           [self.OUTPUT_TENSOR_NAME,
           self.SOFTMAX_TENSOR_NAME],
           feed_dict={self.INPUT_TENSOR_NAME: [np.asarray(image)]})

        seg_map = batch_seg_map[0]        
        #seg_map = resize(seg_map.astype(np.uint8), (height, width), preserve_range=True, order=0, anti_aliasing=False)

        prob_map = batch_prob_map[0]        
        


        return seg_map, prob_map

model = DeepLabModel("models/" + current_model)
i = 0
im_output_path_vis = im_output_path + "visual/"
im_output_path_vis_seg = im_output_path + "visual_segmentation/"

os.makedirs(im_output_path, exist_ok=True)
os.makedirs(im_output_path_vis, exist_ok=True)
os.makedirs(im_output_path_vis_seg, exist_ok=True)
for im_filename_long in glob.glob(im_input_path + '*.jpg'):
    print(i)
    while(executor._work_queue.qsize()>5):
        time.sleep(0.5)
    
    img = Image.open(im_filename_long)
    width, height = img.size
    im_filename = ntpath.basename(im_filename_long)[0:-4]
    seg_map, prob_map = model.run(img)
    
    a = executor.submit(imageio.imsave, im_output_path_vis_seg + im_filename + "segmentation.png",(seg_map*84).astype(np.uint8), compress_level=3)
    a = executor.submit(imageio.imsave, im_output_path_vis + im_filename + "softmax.jpg",(prob_map[:,:,(1,2,0)]*255).astype(np.uint8))
    i=i+1
    
    
while executor._work_queue.qsize():
    print('Queue size: '+str(executor._work_queue.qsize()))
    time.sleep(1)

    executor.shutdown(wait=True)
