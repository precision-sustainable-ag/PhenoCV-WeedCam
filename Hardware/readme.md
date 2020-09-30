# Setting Up

  

The materials list could find in this link

- Tablet Lenovo P10 or M10 / Or another kind of Android Device

- Zhiyun-Tech Telescopic Monopod with Strap. Or similar.

- OAK-D Camera

- Raspberry Pi 4 - Micro SD Card 32GB or bigger.

- Power bank for Camera and Rasberry

- Cables

- Waist Pack

- Tablet Tripod Mount Adapter

- Mini Ball Head #2

- Clean clothing and brush

  

![](https://lh3.googleusercontent.com/sF-2OULf9_fVqfnhT60NtGQupxlni_X0wCSQymPrIxGs5EMFYLj20xkRtd7kBphPj7H2AS64hQ3gagAIL8-LUq4QzZK9_1gXmyLWtwpiMVC97tbsM1OhpW1orWo7-GKVhyvuSX7o)

  

# Step 1 Micro SD Card and O.

  

The Raspberry Pi should work with any compatible Micros SD card, although there are some guidelines that should be followed

  

## SD card size (capacity)

  

For installation of the image installation of Raspbian, the minimum recommended card size is 8GB and the maximun is 64Gb. In this tutorial we will use a micro SD card of 32Gb.

  

## SD card class

  

The card class determines the sustained write speed for the card; a class 4 card will be able to write at 4MBs, whereas a class 10 should be able to attain 10 MBs. We will use a class 10 because it is easier to find it in the market.

  

## Write the OS image on the Raspberry Pi 4

  

Prepare your micro SD card if this one is not new.

  

- Download Raspian Pi Imager.

- Insert micro SD in an adapter and then insert them in your computer (Windows)

- Select Operative System: option “ERASE”.

- Select SD Card: Choose your Micro SD Card

- Click on WRITE to ERASE your Micro SD Card.

  

![](https://lh6.googleusercontent.com/FM2F5eYAUuHJJ_4z6-XqkprHXcsD6DNPKPgac5zNgESF8kC3a-qz_gelQb8o0i_qQQIRTlqZuJ854s9YsJ8yhve8YaZiVcfpGIWlawTFy71ca9ieZoLvHgFV_1gTL3kLeabRV_rX)
 
  

![](https://lh4.googleusercontent.com/EjF5gxjpdhafIYDFGBVkSBFHuqnUmuT0A09c_QA6Zk6JrnVOXwxcUcB2fjwvYfzYHhQS2EH4IBBrR9cN1Bwl8-mwMBVtz3_hKFmvVaRWO3q-EakqxXfZTd9ohbmfD_7BfOL6nifp)
  

- Select the Raspian image file (you have ready in your computer). Selecting “Use Custom” option on the Raspbian Pi Imager.

32GB Micro SD Card: RPi image - 
[https://drive.google.com/file/d/1opjc88wXK4hXJVKsq88MQ2DQLpg-RIg3/view?usp=sharing](https://drive.google.com/file/d/1opjc88wXK4hXJVKsq88MQ2DQLpg-RIg3/view?usp=sharing)

64GB Micro SD Card: RPi image -
[https://drive.google.com/file/d/1xDd6B9zLm1vPm9tYWBqWKqCXVQM3hGcG/view?usp=sharing](https://drive.google.com/file/d/1xDd6B9zLm1vPm9tYWBqWKqCXVQM3hGcG/view?usp=sharing)
  
  

![](https://lh6.googleusercontent.com/FM2F5eYAUuHJJ_4z6-XqkprHXcsD6DNPKPgac5zNgESF8kC3a-qz_gelQb8o0i_qQQIRTlqZuJ854s9YsJ8yhve8YaZiVcfpGIWlawTFy71ca9ieZoLvHgFV_1gTL3kLeabRV_rX)

  

![](https://lh4.googleusercontent.com/P_mNtRbN103GnX4DdrS-W2hSutZT7LPVqwfVYX5z0Y2xnFYvA2H64LznE1GUYvAVRiI9UWHHA8ipbvkOzlr9OVq1PRpMOEVfbeXROx5sF2wfOouUZQoyjjB5LYES0c-DLwSz5iRm)

  

- Select Operative System: option “USE CUSTOM”.

- Select SD Card: Choose your Micro SD Card

- Click on WRITE to write the image file into your Micro SD Card. Could take more than 1 hour.

- This image file has installed: Remote desktop control, TeamViewer, VNC, complete DepthAI framework and its dependencies.

## Start with DephtAI framework


- Install RD Client in you Android Device.

- The RPi has by default this network:

Network name: HUAWEI P10

Password: paularamos

- Configure your device as a hotspot with the previous network settings.

- Check the IP address of the Raspberry, you could find this info directly on your hotspot setting or you could download a IP Scanner just to check the RPi IP to connect with.

- Also you can set up your own network in the RPi, but if you don’t have MiniHDMI cable it could be better if you connect the first time with the network by default. Also take into account you need to create a hotspot on the field.

 - Run the **calibration** process following steps 2,3,4, and 5 on this document:

[https://docs.luxonis.com/tutorials/stereo_calibration/](https://docs.luxonis.com/tutorials/stereo_calibration/)

- In the step number 6, please use this command line.

Type: "python3 depthai_demo.py -brd WEED01 -e"

- To collect data please follow the next steps:

Open the terminal of RPi

Type: “cd depthai”

- If we want to see the a **preview output**. The script launches a window, starts the cameras, and displays a video stream annotated with object localization metadata. But this script does not collect images. It is just to give you an idea about the image could come from the camera.

Type: “python3 depthai_demo.py”

- If you want to run the script to **collect images** please run the next CLI in the terminal.

Type: “./run.sh”

- Check the next path:

/home/pi/depthai/field/data

You could find there a lot of folders with different date and timestamp, inside of every folder you could find another bunch of folders with the same scene with 4 different frames (RGB, left, right, disparity map)

- Also you can play with the API. [https://docs.luxonis.com](https://docs.luxonis.com/tutorials/hello_world/)

## Username: pi
## Password: 0000
