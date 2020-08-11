
## RPi Configuration

**DepthAI framework installation**
https://docs.luxonis.com/api/#raspbian

**Intel Neural Compute Stick 2 (NCS2) installation.**
Some models, such as semantic segmentation and pose estimation, are not yet supported by DepthAI framework, so we must use the VPU as an NCS2, for this we will need to follow the steps documented in the following links:
(Introduction anout NCS2) https://software.intel.com/content/www/us/en/develop/articles/get-started-with-neural-compute-stick.html
https://docs.openvinotoolkit.org/latest/openvino_docs_install_guides_installing_openvino_raspbian.html

"Note To use a Raspberry Pi as the host for the Intel® NCS 2, it’ s recommended that you still follow the getting started instructions on this page to install the full Intel® Distribution of the OpenVINO™ toolkit on one of the supported platforms (Windows, Linux*) and then install the Inference Engine on your Raspberry Pi and review the Raspberry Pi workflow."

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


## Modular camera set up

To set up the hardware, follow the instructions in this document.

https://docs.luxonis.com/products/bw1098ffc/#setup

We have made a case to guarantee minimum depth distance. See description on the wiki page.

Once you have the cameras assembled in this case please follow the calibration instructions.

## Calibration process for our BW1098FFC Camera

For the calibration process follow the instruction in thi link ([https://docs.luxonis.com/tutorials/stereo_calibration/](https://docs.luxonis.com/tutorials/stereo_calibration/)). You can keep depthAI framework to make your calibration process.  
1) For taking images to calculate matrix calibration follow the calibrate.py script instructions, setting up a new board.  
2) Create a json file in depthAI/resources/board with the name of your board e.g WEED01.json.  
3) Put this info into this file:  

{  
    "board_config":  
    {  
        "name": "WEED01",  
        "revision": "0.0",  
        "swap_left_and_right_cameras": true,  
        "left_fov_deg": 71.86,  
        "rgb_fov_deg": 68.7938,  
        "left_to_right_distance_cm": 2.7,  
        "left_to_rgb_distance_cm": 5.4  
    }  
}

4) Run this code in depthAI folder  
`python3 calibrate.py -s SQUARE_SIZE_IN_CM -brd WEED01`.  
5) Then run:  `python3 test.py -s depth_sipp`  
6) A popup window will display with the Disparity Confidence, move the confidence slider until you see less black. 255 means it will accept as most matches as possible, and 1 means it will only accept disparity matches, it is super confident in.  
Once you are satisfied with the results of the calibration using the Disparity Confidence, you should save the calibration data into the camera's EEPROM using the following command line.  
`python3 test.py -brd WEED01.json -e`

Note that the BASELINE distance is 5.4 cm and the RGBLEFT distance is 2.7 cm. Use the file WEED01.json for the configuration of the card and save it in depthAI/resources/board. Perform the calibration process and test the results by running the following command 

`python3 test.py -s depth_sipp`

A popup window will display with the Disparity Confidence, move the confidence slider until you see less black. 255 means it will accept as most matches as possible, and 1 means it will only accept disparity matches, it is super confident in. 

Once you are satisfied with the results of the calibration using the Disparity Confidence, you should save the calibration data into the camera's eeprom using the following command line.

`python3 test.py -brd WEED01.json -e`

Please note that this command line is case sensitive.



## RPi-Testing
