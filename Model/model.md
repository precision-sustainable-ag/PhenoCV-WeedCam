Please use this part of the repository to document all links, process, notebooks, etc.

deeplabv3+
Supplied is :
a compressed tensorflow pb model: 4_class_model_v1.0.pb
a python script to use the model to segment images: deploy.py
three example images and three corresponding outputs.

The four classes translates to: 
0: soil/background, 
1: clover,
2: grass,
3: weeds (mainly dandelion and thistles, but can somewhat generalize to similar species)
