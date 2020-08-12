Please use this part of the repository to document all links, process, notebooks, etc.

### General workflow 
1. Download and convert the frozen tensorflow model (.pb) to an intermediate representation using the Openvino toolkit's model optimizer. (Generates .xml and .bin) files 
2. Use those 2 files to get a .blob file using the MYRIAD_X compiler. 
3. Use the blob files along with the *.json* and *_depth.json* files and run them using the test.py script in depthai to test the model. 

### OAK-D in NCS2 mode 

Before geax's suggestion the models are also being tested in NCS2 mode. 

### Resources used while testing. 

Tutorials for pretrained openvino models. https://docs.luxonis.com/tutorials/openvino_model_zoo_pretrained_model/ 

Custom models and custom data - https://colab.research.google.com/github/luxonis/depthai-ml-training/blob/master/colab-notebooks/Easy_Object_Detection_Demo_Training.ipynb

PINTO Model zoo - https://github.com/PINTO0309/PINTO_model_zoo

PINTO OpenVino - Deeplabv3 - https://github.com/PINTO0309/OpenVINO-DeeplabV3

