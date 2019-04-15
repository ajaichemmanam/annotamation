Semi Automatic annotation for Object Detection.

## How to use?

STEP1:-
Copy partially trained model and pbtxt file to models folder. Run the main python file. Images in the data/dataset folder will be automatically annotated based on the inference of the partially trained model

STEP2:-
Tries to open LabelImg if found in path, Else Open it yourself and verify/Correct the annoations

STEP3:-
Once verified, Specify the number of augmented images per actual image is to be generated.
It uses img aug library. These are some of the parameters used to tweak the Augmentation properties
.. iaa.Multiply((1.2,1.5)), # Adds Brightness, Doesn't Affect Keypoints
.. iaa.Grayscale(alpha=(0.0, 1.0)), # , Doesn't Affect Keypoints # iaa.Dropout((0.01, 0.1), per_channel=0.5)
.. iaa.GaussianBlur((0, 3.0)), #Adds Gausian Blur, Doesn't Affect keypoints
.. iaa.Affine(scale=(0.9, 1.1), #Transforms to 50 % to 110%, Affects keypoints
.. rotate=(-1,0))])

STEP4:-
Give the TEST:TRAIN Ratio, to split the files in data/dataset folder to Test and Train Folders in the given ratio.
The Files to be moved to Test folder is completely random

STEP5:-
Generate CSV Files from the XML files in Test and Train Folders.

STEP6:-
Generate TF Records for Test and Train

STEP7:-
Use these Files for Training the model again. And Repeat the steps as a cycle

## Root Structure

root
|-->models
......|--> frozen_inference_graph.pb (Partially trained model)
......|--> labels.pbtxt (pbtxt for the trained model)
|-->data
......|--> dataset (Images to be annotated has to be copied here. Image Augmentations and Annotations are saved here, before moving to test and train folders)
......|--> test (Files from dataset are moved here according to test:train ratio)
......|--> train (Files from dataset are moved here according to test:train ratio)
......|--> test.csv, train.csv, test.record, train.record (Files generated here)

## Notes:

## Dependencies:

FOR ANNOTATION VERIFICATION
Required LabelImg: https://github.com/tzutalin/labelImg/releases

FOR IMAGE AUGMENTATION

Download appropriate whl file for shapely from this site
https://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely

pip install \*.whl file

pip install imgaug
