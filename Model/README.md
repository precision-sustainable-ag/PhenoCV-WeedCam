## deeplabv3+
Supplied is :
a compressed tensorflow pb model: 4_class_model_v1.0.pb - Download it here: https://drive.google.com/file/d/1tVvFPu79VueEet4P-brgk4ijArm1sUCs/view
a python script to use the model to segment images: deploy.py
three example images and three corresponding outputs.

The four classes translates to: 
0: soil/background, 
1: clover,
2: grass,
3: weeds (mainly dandelion and thistles, but can somewhat generalize to similar species)

Tensorflow 1.15 was used during training. It is most probably needed when translating the deeplabv3+ model to the OAK system.
Deeplabv3+ source code, including installation guidelines, can be found here: https://github.com/tensorflow/models/tree/master/research/deeplab