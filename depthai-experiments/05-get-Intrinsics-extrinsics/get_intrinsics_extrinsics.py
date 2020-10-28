import numpy as np  # numpy - manipulate the packet data returned by depthai
import cv2  # opencv - display the video stream
import depthai  # access the camera and its data packets
print('Using depthai module from: ', depthai.__file__, depthai.__version__)

import consts.resource_paths  # load paths to depthai resources
from time import time


class RealWorldRecon:
    def __init__(self):
        self.scalingfactor=1
        self.lh=device.get_left_homography()
        self.rh=device.get_right_homography()
        self.Al=device.get_left_intrinsic()
        self.Ar=device.get_right_intrinsic()
        self.ro=device.get_rotation()
        self.t=device.get_translation()
        
        self.A_inv=np.linalg.inv(self.Al)
        self.R_inv=np.linalg.inv(self.ro)
        
        self.rwcs=np.zeros((1280,720,3))
    def calculate_XYZ(self,u,v):                                          
        #Solve: From Image Pixels, find World Points
        uv_1=np.array([[u,v,1]], dtype=np.float16)
        uv_1=uv_1.T
        suv_1=self.scalingfactor*uv_1
        xyz_c=self.A_inv.dot(suv_1)
#         print(xyz_c.shape, np.array(self.t).shape)
        xyz_c=xyz_c-np.array(self.t).reshape(-1,1)
        
        XYZ=self.R_inv.dot(xyz_c)
        print(XYZ.shape)
        print(np.matmul(np.linalg.inv(self.rh),suv_1))
        return XYZ
    
    def save_rwc(self):
        for i in range(1280):
            for j in range(720):
                rwc=self.calculate_XYZ(i,j)
                self.rwcs[i,j,0]=rwc[0]
                self.rwcs[i,j,1]=rwc[1]
                self.rwcs[i,j,2]=rwc[2]

    
device = depthai.Device('', False)
p = device.create_pipeline(config={
    "streams": ["previewout", "disparity_color"],
    "ai": {
        "blob_file": consts.resource_paths,
        "blob_file_config": str(Path('./mobilenet-ssd/mobilenet-ssd.json').resolve().absolute())
    },
    'camera': {
        'mono': {
            'resolution_h': 720, 'fps': 30
        },
    },
})

if p is None:
    raise RuntimeError("Error initializing pipelne")

rwc=RealWorldRecon()
lh=rwc.lh
rh=rwc.rh
li=rwc.Al
ri=rwc.Ar
ro=rwc.ro
t=rwc.t

calib_data=np.vstack((lh,rh,li,ri,ro,t))
print(calib_data)
print(rwc.calculate_XYZ(1,2))
print(end='\n')
print(rwc.calculate_XYZ(1280,720))

# Q = np.float32([[1,0,0,0],
#                 [0,-1,0,0],
#                 [0,0,focal_length*0.05,0],
#                 [0,0,0,1]])
# points_3d = cv2.reprojectImageTo3D
