## deeplabv3+
Supplied is :


* A compressed tensorflow pb model: models/3_class_model_v1.2/3_class_model_v1.2.pb - Download it here: https://drive.google.com/file/d/1Xp5_gSbrvuR999oM9CkwS5leNAdOeL0m/view
* A compressed tensorflow pb model: models/4_class_model_v1.0/4_class_model_v1.0.pb - Download it here: https://drive.google.com/file/d/1tVvFPu79VueEet4P-brgk4ijArm1sUCs/view
* A python script to use the model to segment images: deploy.py
* Three example images and corresponding outputs.

The three class model outputs translate to: 
* 0: soil/background, 
* 1: broadleaf weeds,
* 2: grass,

The four class model outputs translate to: 
* 0: soil/background, 
* 1: clover,
* 2: grass,
* 3: weeds (mainly dandelion and thistles, but can somewhat generalize to similar species)

Tensorflow 1.15 was used during training. It is most probably needed when translating the deeplabv3+ model to the OAK system.
Deeplabv3+ source code, including installation guidelines, can be found here: https://github.com/tensorflow/models/tree/master/research/deeplab
