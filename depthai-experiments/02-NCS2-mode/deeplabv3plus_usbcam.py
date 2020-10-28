import sys
import os
import argparse
import numpy as np
import cv2
import time
from PIL import Image
from collections import Counter
try:
    from armv7l.openvino.inference_engine import IENetwork, IECore
except:
    from openvino.inference_engine import IENetwork, IECore

fps = ""
framecount = 0
time1 = 0

# Deeplab color palettes
DEEPLAB_PALETTE = Image.open("colorpalette.png").getpalette()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--deep_model", default="/home/pi/OAK-D-depthai-expts/02-NCS2-mode/FP16/3class_360/3class_360.xml", help="Path of the deeplabv3plus model.")
    parser.add_argument("--input_path", default="image1.png")
    parser.add_argument("--usbcamno", type=int, default=0, help="USB Camera number.")
    parser.add_argument('--camera_width', type=int, default=640, help='USB Camera resolution (width). (Default=640)')
    parser.add_argument('--camera_height', type=int, default=360, help='USB Camera resolution (height). (Default=480)')
    parser.add_argument('--input_width', type=int, default=640, help = 'Model input width')
    parser.add_argument('--input_height', type=int, default=360, help = 'Model input height')
    parser.add_argument('--vidfps', type=int, default=30, help='FPS of Video. (Default=30)')
    parser.add_argument('--device', type=str, default='MYRIAD', help='Specify the target device to infer on; CPU, GPU, FPGA or MYRIAD is acceptable. \
                                                                   Sample will look for a suitable plugin for device specified (CPU by default)')
    args = parser.parse_args()
    deep_model    = args.deep_model
    usbcamno      = args.usbcamno
    camera_width  = args.camera_width
    camera_height = args.camera_height
    vidfps        = args.vidfps
    device        = args.device
#     print(args.model_size[0], args.model_size[1])
    model_xml = deep_model
    model_bin = os.path.splitext(model_xml)[0] + ".bin"

    ie = IECore()
    # print(ie.get_config())
    #ie.add_extension(extension_path="/opt/intel/openvino/inference_engine/lib/intel64/libinference_engine.so", device_name="MYRIAD")
    net = ie.read_network(model_xml, model_bin)
    print(net.input_info)
    input_info = net.input_info
    input_blob = next(iter(input_info))
    exec_net = ie.load_network(network=net, device_name=args.device)

    # cam = cv2.VideoCapture(usbcamno)
    # cam.set(cv2.CAP_PROP_FPS, vidfps)
    # cam.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
    # cam.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)
    # waittime = 1
    # window_name = "USB Camera"

    # cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

    while True:
        t1 = time.perf_counter()
        # ret, color_image = cam.read()
        # if not ret:
        #     continue
        color_image = cv2.imread(args.input_path)
        color_image = cv2.resize(color_image, (camera_width, camera_height))
        # Normalization
        prepimg_deep = cv2.resize(color_image, (args.input_width, args.input_height))
        prepimg_deep = cv2.cvtColor(prepimg_deep, cv2.COLOR_BGR2RGB)
        prepimg_deep = np.expand_dims(prepimg_deep, axis=0)
        prepimg_deep = prepimg_deep.astype(np.float32)
        prepimg_deep = np.transpose(prepimg_deep, [0, 3, 1, 2])
#         prepimg_deep -= 127.5
#         prepimg_deep /= 127.5
        t11=time.perf_counter()
        # Run model - DeeplabV3-plus
        deeplabv3_predictions = exec_net.infer(inputs={input_blob: prepimg_deep})
        t12=time.perf_counter()
        print(t12-t11)
        # Get results
        print(deeplabv3_predictions.keys())
        predictions = deeplabv3_predictions['Cast_2']
        
#         predictions = deeplabv3_predictions['Output/Transpose']
        print(np.array(predictions).shape)
        # import seaborn as sns
        # import matplotlib.pyplot as plt
        # sns.distplot(predictions[0].flatten())
        # plt.show()
        # Segmentation
        # outputimg = np.uint8(predictions[0][0])
        outputimg = np.uint8(predictions[0])
        print(outputimg.shape)
        outputimg = cv2.resize(outputimg, (camera_width, camera_height))
        outputimg = Image.fromarray(outputimg, mode="P")
        outputimg.putpalette(DEEPLAB_PALETTE)
        outputimg = outputimg.convert("RGB")
        outputimg = np.asarray(outputimg)
        outputimg = cv2.cvtColor(outputimg, cv2.COLOR_RGB2BGR)
        cv2.imshow('seg', outputimg)
        imdraw = cv2.addWeighted(color_image, 1.0, outputimg, 0.9, 0)

        cv2.putText(imdraw, fps, (camera_width-170,15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (38,0,255), 1, cv2.LINE_AA)
        # cv2.imshow(window_name, imdraw)
        cv2.imshow('output',imdraw)

        if cv2.waitKey(1)&0xFF == ord('q'):
            break

        # FPS calculation
        framecount += 1
        if framecount >= 10:
            fps       = "(Playback) {:.1f} FPS".format(time1/10)
            framecount = 0
            time1 = 0
        t3 = time.perf_counter()
        elapsedTime = t3-t1
        time1 += 1/elapsedTime
