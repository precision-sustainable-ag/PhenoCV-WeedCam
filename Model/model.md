Please use this part of the repository to document all links, process, notebooks, etc.

### General workflow 
1. Download and convert the frozen tensorflow model (.pb) to an intermediate representation using the Openvino toolkit's model optimizer. (Generates .xml and .bin) files 

The model tested as of now is the deeplab_v3_plus_mnv3_decoder_256.pb from PINTO's repository. 
- Model Optimizer : `python3 /opt/intel/openvino/deployment_tools/model_optimizer/mo_tf.py   --input_model deeplab_v3_plus_mnv2_aspp_decoder_256.pb   --model_name deeplab_v3_plus_mnv2_aspp_decoder_256 --mean_values [127.5,127.5,127.5] --scale_values [127.5,127.5,127.5] --reverse_input_channels  --input_shape [1,256,256,3]   --data_type FP16   --output_dir openvino/256x256/FP16`
- Note that the input needs to be standardized and hence, the mean_values and scale_values arguments need to be given and also the input_channels need to be reversed. 
- Model optimizer help can be brought up with the `--help` argument to the code. The generic `mo.py` can also be used instead of `mo_tf.py` to deal with other kind of models. 

2. Use those 2 files to get a .blob file using the MYRIAD_X compiler. 
- Export Myriad compiler environment variable : `export MYRIAD_COMPILE=$(find /opt/intel/ -iname myriad_compile)`
- Compile the .xml and .bin files into an input .blob file: `$MYRIAD_COMPILE -m  ~<Path/to/xml> -ip U8 -VPU_MYRIAD_PLATFORM VPU_MYRIAD_2480 -VPU_NUMBER_OF_SHAVES 4 -VPU_NUMBER_OF_CMX_SLICES 4`

 
3. Use the blob files along with the *.json* and *_depth.json* files and run them using the test.py script in depthai to test the model. 
- This is the .json used for the person segmentation 
```
{
    "tensors":
    [
        {
            "output_tensor_name": "out",
            "output_dimensions": [1, 1, 256, 256],
            "output_entry_iteration_index": 0,
            "output_properties_dimensions": [0],
            "property_key_mapping": [],
            "output_properties_type": "f16"
        }
    ]
}
```


### OAK-D in NCS2 mode 

Before geax's suggestion the models are also being tested in NCS2 mode. 

For that you need to install OpenVINO. https://docs.openvinotoolkit.org/latest/openvino_docs_install_guides_installing_openvino_raspbian.html

Test the installation running these CLI: 

- Compile: `cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS="-march=armv7-a" /opt/intel/openvino/deployment_tools/inference_engine/samples/cpp`

- Download the openVINO model (bin-xml): `wget --no-check-certificate https://download.01.org/opencv/2019/open_model_zoo/R3/20190905_163000_models_bin/face-detection-retail-0004/FP16/face-detection-retail-0004.bin`
`wget --no-check-certificate https://download.01.org/opencv/2019/open_model_zoo/R3/20190905_163000_models_bin/face-detection-retail-0004/FP16/face-detection-retail-0004.xml`

- Run the code using the camera as NCS2 but with saved images: `./armv7l/Release/object_detection_sample_ssd -m face-detection-retail-0004.xml -d MYRIAD -i IMAGE.jpg`


### Resources used while testing. 

Tutorials for pretrained openvino models. https://docs.luxonis.com/tutorials/openvino_model_zoo_pretrained_model/ 

Custom models and custom data - https://colab.research.google.com/github/luxonis/depthai-ml-training/blob/master/colab-notebooks/Easy_Object_Detection_Demo_Training.ipynb

PINTO Model zoo - https://github.com/PINTO0309/PINTO_model_zoo

PINTO OpenVino - Deeplabv3 - https://github.com/PINTO0309/OpenVINO-DeeplabV3

