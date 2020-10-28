"""! @brief script for annotating data

"""

import cv2
import numpy as np
import os
import argparse
import pickle

biomass_availability = [
    '2020_10_09_10_22_21',
    '2020_10_09_10_22_57',
    '2020_10_09_10_35_10',
    '2020_10_09_10_35_43',
    '2020_10_09_10_42_33',
    '2020_10_09_10_43_20',
    '2020_10_09_10_52_09',
    '2020_10_09_10_52_40',
    '2020_10_09_10_59_08',
    '2020_10_09_11_00_34',
    '2020_10_09_11_07_13',
    '2020_10_09_11_08_47',
    '2020_10_09_11_15_26',
    '2020_10_09_11_16_44',
    '2020_10_09_11_27_14',
    '2020_10_09_11_27_55',
    '2020_10_09_11_33_58',
    '2020_10_09_11_34_38',
    '2020_10_09_11_40_49',
    '2020_10_09_11_41_47',
    '2020_10_09_11_47_33',
    '2020_10_09_11_48_22'
]

data_dir = '/home/jeff/Data/ARoS/Fall-Independent-Study/NC_10_09_2020/'
annotate_point_set = []


def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument('--path', action='store', required=False)
    return args.parse_args()

def get_annotatable_directories(data_dir):
    global biomass_availability
    annotatable = []
    for root, dirs, _ in os.walk(data_dir):
        for d in dirs:
            if d in biomass_availability:
                path = os.path.join(root, d)

                images = [os.path.join(path, f) for f in os.listdir(path) if os.path.isdir(os.path.join(path,f))]
                images = [f for f in images if ('depth.npy' in os.listdir(f)) and ('color.png' in os.listdir(f)) and not('box_annotation.pkl') in os.listdir(f)]
                annotatable.extend(images)
    return (n for n in annotatable)

def select_point(event, i , j, flags, param):
    if event == cv2.EVENT_LBUTTONDBLCLK: ## double click
        annotate_point_set.append((i,j))


def construct_gui():
    cv2.namedWindow("Annotate GUI", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Annotate GUI", select_point)


def main():
    global data_dir, annotate_point_set
    args = parse_args()
    if args.path:
        data_dir = args.path

    annotatable = get_annotatable_directories(data_dir)

    image_basepath = next(annotatable)

    construct_gui()
    color_path = os.path.join(image_basepath, 'color.png')
    depth_path = os.path.join(image_basepath, 'depth.npy')
    print(color_path)
    color = True
    while True:
        #Rendering
        if color:
            img = cv2.imread(color_path)
            for point_set in annotate_point_set:
                cv2.circle(img, point_set, 30, (255,0,0), 4)
            cv2.imshow('Annotate GUI', img)
        else:
            data = np.load(depth_path)
            data = data.astype(np.float64)
            data[data!=data] = 0 # get rid of nans
            data[data == 65535] = 0
            data /= data.max()
            data *= 255
            data = data.astype('uint8')
            hmap = cv2.applyColorMap(data, cv2.COLORMAP_JET)
            cv2.imshow('Annotate GUI', hmap)
        
        # Control Logic
        k = cv2.waitKey(1) & 0xFF

        if k == 113: # q
            break
        elif k == 100: # d
            color = not color
        elif k == 112: # p
            if annotate_point_set:
                annotate_point_set.pop()
        elif k == 114: #r
            annotate_point_set = []
        elif k == 115: #s
            with open(os.path.join(image_basepath, 'box_annotation.pkl'), 'wb') as f:
                pickle.dump(annotate_point_set, f)
            print(f'saved box annotations at {os.path.join(image_basepath, "box_annotation.pkl")}')
            image_basepath = next(annotatable)
            color_path = os.path.join(image_basepath, 'color.png')
            depth_path = os.path.join(image_basepath, 'depth.npy')
            annotate_point_set = []
            
        elif k == 98:
            image_basepath = next(annotatable)
            color_path = os.path.join(image_basepath, 'color.png')
            depth_path = os.path.join(image_basepath, 'depth.npy')
            annotate_point_set = []
            print('skipped bad image')      
    
    cv2.destroyAllWindows()

        


if __name__ == "__main__":
    main()