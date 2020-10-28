import argparse
from pathlib import Path
from multiprocessing import Process
from uuid import uuid4
import json

import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import consts.resource_paths
import cv2
import depthai

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', default="data", type=str, help="Path where to store the captured data")
parser.add_argument('-d', '--dirty', action='store_true', default=False, help="Allow the destination path not to be empty")
args = parser.parse_args()

device = depthai.Device()

dest = Path(args.path).resolve().absolute()
if dest.exists() and len(list(dest.glob('*'))) != 0 and not args.dirty:
    raise ValueError(f"Path {dest} contains {len(list(dest.glob('*')))} files. Either specify new path or use \"--dirty\" flag to use current one")
dest.mkdir(parents=True, exist_ok=True)

config={
    "streams": ["previewout", "depth_raw"],
    'depth':
    {
        'calibration_file': consts.resource_paths.calib_fpath,
        'left_mesh_file': consts.resource_paths.left_mesh_fpath,
        'right_mesh_file': consts.resource_paths.right_mesh_fpath,
        'padding_factor': 0.3,
        'depth_limit_m': 10.0, # In meters, for filtering purpose during x,y,z calc
        'confidence_threshold' : 0.5, #Depth is calculated for bounding boxes with confidence higher than this number
        'median_kernel_size': 7,
        'lr_check': False,
        'warp_rectify':
        {
            'use_mesh' : False, # if False, will use homography
            'mirror_frame': True, # if False, the disparity will be mirrored instead
            'edge_fill_color': 0, # gray 0..255, or -1 to replicate pixel values
        },
    },
    "ai":{
        "blob_file": consts.resource_paths.blob_fpath,
        "blob_file_config": consts.resource_paths.blob_config_fpath
    },
    'camera':
    {
        'rgb':
        {
            # 3840x2160, 1920x1080
            # only UHD/1080p/30 fps supported for now
            'resolution_h': 1080,
            'fps': 30,
        },
        'mono':
        {
            # 1280x720, 1280x800, 640x400 (binning enabled)
            'resolution_h': 720,
            'fps': 30,
        },
    },
}

p = device.create_pipeline(config=config)
if p is None:
    raise RuntimeError("Error initializing pipelne")

procs = []

def store_frames(depth_raw, depth_img):
    global saved_frame_ct
    global procs
    frames_path = dest / Path(str(uuid4()))
    frames_path.mkdir(parents=False, exist_ok=False)
    new_procs = [
        Process(target=cv2.imwrite, args=(str(frames_path / Path("depth_raw.png")), depth_img)),
        Process(target=np.save, args=(str(frames_path / Path("depth_raw.npy")), depth_raw)),
    ]
    for proc in new_procs:
        proc.start()
    procs += new_procs

def on_trackbar_change(value):
    device.send_disparity_confidence_threshold(value)
    return

cv2.namedWindow('depth_raw')
trackbar_name = 'Disparity confidence'
conf_thr_slider_min = 0
conf_thr_slider_max = 255
cv2.createTrackbar(trackbar_name, 'depth_raw', conf_thr_slider_min, conf_thr_slider_max, on_trackbar_change)
cv2.setTrackbarPos(trackbar_name, 'depth_raw', 255)


# device.send_DisparityConfidenceThreshold(255)
saved_frame_ct=0
while True:
    data_packets = p.get_available_data_packets(True)
    for packet in data_packets:
        if packet.stream_name == 'previewout':
            data = packet.getData()
            data0 = data[0, :, :]
            data1 = data[1, :, :]
            data2 = data[2, :, :]
            rgb = cv2.merge([data0, data1, data2])
            cv2.imshow('previewout', rgb)
        elif packet.stream_name == "depth_raw":
            depth_raw_frame=packet.getData()
            #for visualizing.
            depth_raw_frame_img = (65535 // depth_raw_frame).astype(np.uint8)
            #colorize depth map, comment out code below to obtain grayscale
            depth_raw_frame_img = cv2.applyColorMap(depth_raw_frame_img, cv2.COLORMAP_HOT)
            cv2.imshow('depth_raw', depth_raw_frame_img)

            store_frames(depth_raw_frame, depth_raw_frame_img)
            saved_frame_ct+=1

    if saved_frame_ct>10:
        break
    if cv2.waitKey(1) == ord('q'):
        break
del p

# depthai.deinit_device()
frames=[]
for dirName, subdirList, fileList in os.walk(dest):
    print('Found directory: %s' % dirName)
    for fname in fileList:
        if '.npy' in fname:
            print('\t%s' % fname)
            frames.append(np.load(dirName+'/'+fname))

xyz=[]

for i in range(frames[-1].shape[0]):
    for j in range(frames[-1].shape[1]):
        xyz.append((i,j,frames[-1][i][j]))

print(np.array(xyz)[:,:2].shape)
xyz=np.array(xyz)
df=pd.DataFrame(xyz, columns=['x','y','z'])
print(df.tail())
dropz=df.index[df['z']==0].tolist()
dropi=df.index[df['z']==65535].tolist()
c=dropz+dropi
df=df.drop(df.index[c])
print(df.shape)
df_o = df[df['z'] < df['z'].quantile(0.90)]
print(df_o.shape)

xyz=df_o.to_numpy()
plt.figure()
ax = plt.subplot(111, projection='3d')
ax.scatter(xyz[:,0], xyz[:,1], xyz[:,2], color='b')

A = np.matrix(np.c_[xyz[:,0], xyz[:,1], np.ones(xyz.shape[0])])
b = np.matrix(xyz[:,2]).T
fit = (A.T * A).I * A.T * b
errors = b - A * fit
residual = np.linalg.norm(errors)

print("solution:")
print("%f x + %f y + %f = z" % (fit[0], fit[1], fit[2]))
print("errors:")
print(errors)
print("residual:")
print(residual)
print("rmse")
print(np.sqrt((np.multiply(np.array(errors), np.array(errors))).mean()))

# plot plane
xlim = ax.get_xlim()
ylim = ax.get_ylim()
X,Y = np.meshgrid(np.arange(xlim[0], xlim[1]),
                  np.arange(ylim[0], ylim[1]))
Z = np.zeros(X.shape)
for r in range(X.shape[0]):
    for c in range(X.shape[1]):
        Z[r,c] = fit[0] * X[r,c] + fit[1] * Y[r,c] + fit[2]
ax.plot_wireframe(X,Y,Z, color='k')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
plt.show()