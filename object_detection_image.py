
import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile

from distutils.version import StrictVersion
from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image
import cv2
from utilities.utils import ops as utils_ops

from utilities.utils import label_map_util
from utilities.utils import visualization_utils as vis_util

# Import Classes
from utilities.classes import labelItem, fileProperties

#  Import Find Objects
from utilities.findObjects import findObjects

# Import Generate XMl utility
from utilities.generateXML import generateXML

# Import Image Augmentation utility
from utilities.generateAugmentedImages import generateAugmented

# Import Prompt
from utilities.prompt import promptInput, promptInt, promptRatio

# Import File utilities
from utilities.fileUtilities import splitTestTrainFiles

# Convert XML to CSV Utility
from utilities.xml_to_csv import convertXML2CSV

# Generate TF Record utility
from utilities.generate_TFRecord import generateTFRecord

labelImgPath = 'E:\Tensorflow\labelImgRelease\labelImg.exe'
# Supported files for Inference and Annotation
supportedfiles = ["jpg", "jpeg", "png", "bmp"]
initLabels = {}

trainDir = 'data/train'
testDir = 'data/test'


def run_inference_for_single_image(image, graph):
    with graph.as_default():
        with tf.Session() as sess:
            # Get handles to input and output tensors
            ops = tf.get_default_graph().get_operations()
            all_tensor_names = {
                output.name for op in ops for output in op.outputs}
            tensor_dict = {}
            for key in [
                'num_detections', 'detection_boxes', 'detection_scores',
                'detection_classes', 'detection_masks'
            ]:
                tensor_name = key + ':0'
                if tensor_name in all_tensor_names:
                    tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
                        tensor_name)

            if 'detection_masks' in tensor_dict:
                # The following processing is only for single image
                detection_boxes = tf.squeeze(
                    tensor_dict['detection_boxes'], [0])
                detection_masks = tf.squeeze(
                    tensor_dict['detection_masks'], [0])
                # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
                real_num_detection = tf.cast(
                    tensor_dict['num_detections'][0], tf.int32)
                detection_boxes = tf.slice(detection_boxes, [0, 0], [
                                           real_num_detection, -1])
                detection_masks = tf.slice(detection_masks, [0, 0, 0], [
                                           real_num_detection, -1, -1])
                detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                    detection_masks, detection_boxes, image.shape[0], image.shape[1])
                detection_masks_reframed = tf.cast(
                    tf.greater(detection_masks_reframed, 0.5), tf.uint8)
                # Follow the convention by adding back the batch dimension
                tensor_dict['detection_masks'] = tf.expand_dims(
                    detection_masks_reframed, 0)
            image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

            # Run inference
            output_dict = sess.run(tensor_dict,
                                   feed_dict={image_tensor: np.expand_dims(image, 0)})

            # all outputs are float32 numpy arrays, so convert types as appropriate
            output_dict['num_detections'] = int(
                output_dict['num_detections'][0])
            output_dict['detection_classes'] = output_dict[
                'detection_classes'][0].astype(np.uint8)
            output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
            output_dict['detection_scores'] = output_dict['detection_scores'][0]
            if 'detection_masks' in output_dict:
                output_dict['detection_masks'] = output_dict['detection_masks'][0]
    return output_dict


PATH_TO_FROZEN_GRAPH = 'models/frozen_inference_graph.pb'
PATH_TO_LABELS = os.path.join('./models', 'labels.pbtxt')

detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

##category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)
category_index = label_map_util.create_category_index_from_labelmap(
    PATH_TO_LABELS)

for key in category_index.keys():
    initLabels[key] = category_index[key]["name"]
#cap = cv2.VideoCapture(0)

path = "data/dataset"
filesCount = len(os.listdir(path))
print("Total Files to Annotate: ", filesCount)
count = 0
filepaths = [os.path.join(path, f) for f in os.listdir(path)]

with detection_graph.as_default():
    with tf.Session() as sess:
        for filepath in filepaths:
            # while True:
            count += 1
            print("Annotating files... {0} of {1}".format(count, filesCount))
            _, filename = os.path.split(filepath)
            folder = os.path.dirname(filepath)
            filesplit = filename.split(".")
            if filesplit[len(filesplit)-1] in supportedfiles:
                #ret,image = cap.read()
                # Get File Properties
                image = cv2.imread(filepath)
                imageHeight, imageWidth, imageChannels = image.shape
                imageSize = os.path.getsize(filepath)

                fileProps = fileProperties(
                    filename, folder, filepath, imageWidth, imageHeight, imageChannels, imageSize)
                # print("file", filepath, "folder", folder, "imgHeight", imageHeight, "imgWidth", imageWidth,
                #       "imgChannel", imageChannels, "imgSize", imageSize)

                # Get handles to input and output tensors
                ops = tf.get_default_graph().get_operations()
                all_tensor_names = {
                    output.name for op in ops for output in op.outputs}
                tensor_dict = {}
                for key in [
                    'num_detections', 'detection_boxes', 'detection_scores',
                    'detection_classes', 'detection_masks'
                ]:
                    tensor_name = key + ':0'
                    if tensor_name in all_tensor_names:
                        tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
                            tensor_name)
                if 'detection_masks' in tensor_dict:
                    # The following processing is only for single image
                    detection_boxes = tf.squeeze(
                        tensor_dict['detection_boxes'], [0])
                    detection_masks = tf.squeeze(
                        tensor_dict['detection_masks'], [0])
                    # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
                    real_num_detection = tf.cast(
                        tensor_dict['num_detections'][0], tf.int32)
                    detection_boxes = tf.slice(detection_boxes, [0, 0], [
                        real_num_detection, -1])
                    detection_masks = tf.slice(detection_masks, [0, 0, 0], [
                        real_num_detection, -1, -1])
                    detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                        detection_masks, detection_boxes, image.shape[0], image.shape[1])
                    detection_masks_reframed = tf.cast(
                        tf.greater(detection_masks_reframed, 0.5), tf.uint8)
                    # Follow the convention by adding back the batch dimension
                    tensor_dict['detection_masks'] = tf.expand_dims(
                        detection_masks_reframed, 0)
                image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

                # Run inference
                output_dict = sess.run(tensor_dict,
                                       feed_dict={image_tensor: np.expand_dims(image, 0)})

                # all outputs are float32 numpy arrays, so convert types as appropriate
                output_dict['num_detections'] = int(
                    output_dict['num_detections'][0])
                output_dict['detection_classes'] = output_dict[
                    'detection_classes'][0].astype(np.uint8)
                output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
                output_dict['detection_scores'] = output_dict['detection_scores'][0]
                if 'detection_masks' in output_dict:
                    output_dict['detection_masks'] = output_dict['detection_masks'][0]

                #output_dict = run_inference_for_single_image(image_np, detection_graph)
                # Find Objects detected for writing to XML
                objectList = findObjects(output_dict['detection_boxes'], output_dict['detection_classes'],
                                         output_dict['detection_scores'], category_index)
                # Generate XML
                generateXML(fileProps, objectList)
                # Draw boxes
                vis_util.visualize_boxes_and_labels_on_image_array(
                    image,
                    output_dict['detection_boxes'],
                    output_dict['detection_classes'],
                    output_dict['detection_scores'],
                    category_index,
                    instance_masks=output_dict.get('detection_masks'),
                    use_normalized_coordinates=True,
                    line_thickness=8)
                # Save the images with boxes
                #cv2.imwrite("data/testOutput/"+filename, image)
            else:
                print("Skipping Unsupported File: ", filename)

print("All Images have been annotated. Please verify before Augmentation")
openLabelImg = promptInput("Open labalImg Tool?")
if(openLabelImg):
    if(os.path.isfile(labelImgPath)):
        os.system(labelImgPath)
    else:
        print("Incorrect path to LabelImg/ Missing. Open LabelImg yourself and verify the dataset before proceeding")

verified = promptInput("Verified XMl Files?")
if(verified):
    numImgGen = promptInt(
        "How many augmented Images have to be generated per Image?")
    # Generate Image Augmented File @Params Origin Directory , Destination Directory, Number of Images to be generated
    generateAugmented("data\dataset", "data\dataset", numImgGen)

testPercentage, trainPercentage = promptRatio("Give Test:Train Ratio. ")
hasSplit = splitTestTrainFiles(path, testDir, trainDir,
                               testPercentage, trainPercentage)
csvpaths = []
if(hasSplit):
    print("Files split to Test and Train Folders")
    genCSV = promptInput("Convert to Test and Train CSV Files?")
    if(genCSV):
        csvpaths = convertXML2CSV('data')

proceed = promptInput("Generate TF Records?")
if(proceed):
    for csvpath in csvpaths:
        if (os.path.isfile(csvpath)):
            generateTFRecord('data/train', category_index,
                             csvpath, 'data/train.record')
