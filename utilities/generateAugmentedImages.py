import os
import cv2
import sys
import traceback
import imgaug as ia
from imgaug import augmenters as iaa
import numpy as np
import shutil
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
# Import Matlib for Visualizing Image Augmentation
import matplotlib
matplotlib.use('tkagg')
# Import Classes
from utilities.classes import labelItem, fileProperties, returnObject
# Import Generate XMl utility
from utilities.generateXML import setAugAnnotationXML, getAnnotaitonXML

directory = ''
destdir = ''
supportedfiles = ["jpg", "jpeg", "png", "bmp"]

def dataAugment(origimgfilepath, annofilepath, objectList, numImgGen, destdir):
	try:
		images = []
		image = cv2.imread(origimgfilepath)
		imgpath, imgname = os.path.split(origimgfilepath)
		annopath, annoname = os.path.split(annofilepath)
		keypoints_on_images = []
		keypoints = []
		objclassprocessed = []
		
		#Add keypoints for all Objects
		for labelItem in objectList:
			key = str(labelItem.label)
			xmin = float(labelItem.xmin)
			ymin = float(labelItem.ymin)
			xmax = float(labelItem.xmax)
			ymax = float(labelItem.ymax)
			objclassprocessed.append(key)
			x = xmin
			y = ymin
			keypoints.append(ia.Keypoint(x=x, y=y))
			x = xmax
			y = ymax
			keypoints.append(ia.Keypoint(x=x, y=y))
			x = xmin
			y = ymax
			keypoints.append(ia.Keypoint(x=x, y=y))
			x = xmax
			y = ymin
			keypoints.append(ia.Keypoint(x=x, y=y))
		keypoints_on_images.append(ia.KeypointsOnImage(keypoints, shape=image.shape))
		# Generate required number of Images
		for i in range(0,numImgGen):
			images.append(image)
			keypoints_on_images.append(ia.KeypointsOnImage(keypoints, shape=image.shape))
		# Add Image Augmentation Properties
		seq = iaa.Sequential([
			# iaa.Multiply((1.2,1.5)), # Adds Brightness, Doesn't Affect Keypoints
			# iaa.Grayscale(alpha=(0.0, 1.0)), # , Doesn't Affect Keypoints
			# iaa.Dropout((0.01, 0.1), per_channel=0.5)
			iaa.GaussianBlur((0, 3.0)), #Adds Gausian Blur, Doesn't Affect keypoints
			iaa.Affine(scale=(0.9, 1.1), #Transforms to 50 % to 110%, Affects keypoints
			rotate=(-1,0))])
		# Make our sequence deterministic.
		# We can now apply it to the image and then to the keypoints and it will
		# lead to the same augmentations.
		# IMPORTANT: Call this once PER BATCH, otherwise you will always get the
		# exactly same augmentations for every batch!
		seq_det = seq.to_deterministic()
		
		# Augment keypoints and images
		images_aug = seq_det.augment_images(images)
		keypoints_aug = seq_det.augment_keypoints(keypoints_on_images)
		# print("images_aug", images_aug)
		# print("keypoints_aug", keypoints_aug)
		
		# Globally Modified keypoints and Index
		# gblmodifiedkeypoints = {}
		# gblidx = 1 

		# Example code to show each image and print the new keypoints coordinates
		for img_idx, (image_before, image_after, keypoints_before, keypoints_after) in enumerate(zip(images, images_aug, keypoints_on_images, keypoints_aug)):
			image_before = keypoints_before.draw_on_image(image_before)
			image_after = keypoints_after.draw_on_image(image_after)

			# Write Augmented Image to a file
			image_after_name = '_Augmented_' +str(img_idx) + imgname
			image_after_path = os.path.join(destdir, image_after_name)
			cv2.imwrite(image_after_path, image_after)
			# Image File Props
			imgSize = os.path.getsize(image_after_path)
			imgHeight, imgWidth, imgChannel = image_after.shape
			fileProps = fileProperties(image_after_name, destdir, image_after_path, imgWidth, imgHeight, imgChannel, imgSize)

			# Show Image Before And After Augmentation
			# ia.imshow(np.concatenate((image_before, image_after), axis=1)) # before and after

			# Print All the Keypoints for each of the images
			# for kp_idx, keypoint in enumerate(keypoints_after.keypoints):
			# 	keypoint_old = keypoints_on_images[img_idx].keypoints[kp_idx]
			# 	x_old, y_old = keypoint_old.x, keypoint_old.y
			# 	x_new, y_new = keypoint.x, keypoint.y
			# 	print("[Keypoints for image #%d] before aug: x=%d y=%d | after aug: x=%d y=%d" % (img_idx, x_old, y_old, x_new, y_new))
		
			#Convert Keypoints back to Image Co-ordinates to be written to XML
			modifiedrect = []
			modifiedkeypoints = {}
			idx = 1 
			cntr = 1
			print("Generating Augmented Image {} of {} for {}".format(img_idx + 1, len(images), imgname))
			for kp_idx, keypoint in enumerate(keypoints_after.keypoints):
				x_new, y_new = keypoint.x, keypoint.y
				modifiedrect.append([int(x_new), int(y_new)])
				cntr += 1
				if (cntr > 4):
					modifiedkeypoints[idx] = modifiedrect
					modifiedrect = []
					cntr =1
					idx += 1
			# objclassidx = 0
			objectList = []
			# print("Total Processed",len(objclassprocessed))
			for key, modkey in modifiedkeypoints.items():
				newimgrect = getImgRect(image_after_path,modkey)
				# objclassidx += 1
				# objclassidex = int(objclassidx) % len(objclassprocessed)
				# objclass = objclassprocessed[objclassidex]
				objclass = objclassprocessed[key-1]
				# print("Label", objclass,"Rectangle", newimgrect)
				labelObject = returnObject(objclass, newimgrect[0], newimgrect[1], newimgrect[2], newimgrect[3])
				objectList.append(labelObject)
			setAugAnnotationXML(fileProps, objectList)
	except Exception as e:
		print("Error" + str(e))
		print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))

def getImgRect(imgfilepath,coordlist):
	xmin = ymin = xmax = ymax = ''
	try:
		img = cv2.imread(imgfilepath)
		vrx = np.array(coordlist, np.int32)
		vrx = vrx.reshape((-1,1,2))
		# img = cv2.polylines(img, [vrx], True, (0,255,255),3)
		# get the min area rect
		# rect = cv2.minAreaRect(vrx)
		# box = cv2.boxPoints(rect)
		# convert all coordinates floating point values to int
		# box = np.int0(box)
		# draw a red 'nghien' rectangle
		# cv2.drawContours(img, [box], 0, (0, 0, 255),2)
		# cv2.drawContours(img, [vrx], 0, (0, 0, 255),2)
		# get the bounding rect
		# x, y, w, h = cv2.boundingRect(box)
		x, y, w, h = cv2.boundingRect(vrx)
		# print("x, y, w, h",x, y, w, h)
		# Draw a green rectangle to visualize the bounding rect
		# cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
		# cv2.imshow('Draw01',img)
		# cv2.waitKey(0)
		xmin = x
		ymin = y
		xmax = x+w
		ymax = y+h
	except Exception as e:
		print("error occured in getting augumented images")
		print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
		print(e)

	return([xmin, ymin, xmax, ymax])

def generateAugmented(origin, destination, numImages):
	directory = origin
	destdir = destination
	filepaths = [os.path.join(origin, f) for f in os.listdir(origin)]
	for filepath in filepaths:
		# print("file", filepath)
		_, imgfilename = os.path.split(filepath)
		filesplit = imgfilename.split(".")
		if filesplit[len(filesplit)-1] in supportedfiles: 
			annofilename = ''
			annofilename = imgfilename
			annofilename = annofilename.replace(str("."+filesplit[len(filesplit)-1]),'.xml')
			origimgfilepath = os.path.join(directory, imgfilename)
			annofilepath = os.path.join(directory, annofilename)
			# print("annofilepath", annofilepath, "origfilepath", origimgfilepath)
			fileProps, objectList =  getAnnotaitonXML(annofilepath)
			dataAugment(origimgfilepath, annofilepath,objectList, numImages, destdir)