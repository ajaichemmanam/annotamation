import os
import cv2
import sys, traceback
import imgaug as ia
from imgaug import augmenters as iaa
import numpy as np
import shutil
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

# objclasslist = [ 'person','bag']
# directory = 'dataset/trianImages'
# destdir = 'dataset/trianImages'
objclasslist = []
directory = ''
destdir = ''
supportedfiles = ["jpg", "jpeg", "png", "bmp"]
numImgGen = 10
gblcoorddict = {}
gbldebug = True


def getAnnoCoord(xmlpath, classnamelist):
	
	try:
		coorddict = {}
		tree = ET.ElementTree(file=xmlpath)
		root = tree.getroot()
		tagname = 'object'
		classtag = 'name'
		#classname = classname
		bboxtag = 'bndbox'
		for classname in classnamelist:
			if (gbldebug): print(classname)
			#print (elem.tag, elem.attrib,elem.text)
			xmin = ymin = xmax = ymax = ''
			coordlist = []
			coordlist.append(xmin)
			coordlist.append(ymin)
			coordlist.append(xmax)
			coordlist.append(ymax)
			coorddict[classname] = coordlist
			for elem in tree.iter(tag=tagname.lower()):
				getbbox = False
				
				for child_of_root in elem:
					if (gbldebug): print (child_of_root.tag, child_of_root.text)
					if (child_of_root.tag == classtag.lower() and child_of_root.text == classname.lower()):
						getbbox = True
					if (getbbox == True and child_of_root.tag == bboxtag.lower()):
						for coord in child_of_root:
							coordtag = coord.tag
							if coordtag.lower() == "xmin":
								xmin = coord.text
							elif coordtag.lower() == "ymin":
								ymin = coord.text
							elif coordtag.lower() == "xmax":
								xmax = coord.text
							elif coordtag.lower() == "ymax":
								ymax = coord.text
							else :
								if (gbldebug): print("co-ordinate not found")
								xmin = ymin = xmax = ymax = ''
								#break
						coordlist = []
						coordlist.append(xmin)
						coordlist.append(ymin)
						coordlist.append(xmax)
						coordlist.append(ymax)
						coorddict[classname] = coordlist
						if (gbldebug): print('coorddict ',coorddict[classname])
						
	#gblcoorddict = coorddict
	except Exception as e:
		print("error occured in getting annotation co-ordinates")
		print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
		print(e)
	
	return coorddict
	
def setAnnoCoord(xmlpath, classname, coordlist):
	xmin = ymin = xmax = ymax = ''
	try:
		tree = ET.ElementTree(file=xmlpath)
		root = tree.getroot()
		tagname = 'object'
		classtag = 'name'
		classname = classname
		bboxtag = 'bndbox'
		#xmin = ymin = xmax = ymax = ''
		checklist = []
		returnval = False
		for elem in tree.iter(tag=tagname.lower()):
			#print (elem.tag, elem.attrib,elem.text)
			getbbox = False
			for child_of_root in elem:
				#print (child_of_root.tag, child_of_root.attrib)
				if (child_of_root.tag == classtag.lower() and child_of_root.text == classname.lower()):
					getbbox = True
				if (getbbox == True and child_of_root.tag == bboxtag.lower()):
					for coord in child_of_root:
						coordtag = coord.tag
						if coordtag.lower() == "xmin":
							coord.text = str(coordlist[0])
							checklist.append(1)
						elif coordtag.lower() == "ymin":
							coord.text = str(coordlist[1])
							checklist.append(2)
						elif coordtag.lower() == "xmax":
							coord.text = str(coordlist[2])
							checklist.append(3)
						elif coordtag.lower() == "ymax":
							coord.text = str(coordlist[3])
							checklist.append(4)
						else :
							if (gbldebug): print("co-ordinate not found")
							xmin = ymin = xmax = ymax = ''
							break
		#set filename and path tag values
		annopath, annoname = os.path.split(xmlpath)
		imgname = annoname
		imgname = imgname.replace('.xml','.jpg')
		imgfilepath = os.path.join(annopath, imgname)
		file_name = root.find('filename')
		file_name.text = imgname
		path = root.find('path')
		path.text = str(imgfilepath)
		if sumList(checklist) == 10:
			tree.write(xmlpath)
			returnval = True
		else :
			print("Error while setting the co-ordinates of annotated xml, kindly check annotation of file ",xmlpath)
	except Exception as e:
		print("error occured in getting annotation co-ordinates")
		print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
		print(e)
	
	return(returnval)
	
def sumList(numbers):
    total = 0
    for x in numbers:
        total += x
    return total

def dataAugment(origimgfilepath,annofilepath,coorddict,destdir):
	try:
		images = []
		image = cv2.imread(origimgfilepath)
		imgpath, imgname = os.path.split(origimgfilepath)
		annopath, annoname = os.path.split(annofilepath)
		keypoints_on_images = []
		keypoints = []
		objclassprocessed = []
		
		for key, coordlist in coorddict.items():
			if (gbldebug): print(key)
			
			if(coordlist[0] != '' and coordlist[1] != '' and coordlist[2] != '' and coordlist[3] != ''):
				if (gbldebug): print('cordlist ',coordlist)
				objclassprocessed.append(key)
				x = coordlist[0]
				y = coordlist[1]
				keypoints.append(ia.Keypoint(x=x, y=y))
				x = coordlist[2]
				y = coordlist[3]
				keypoints.append(ia.Keypoint(x=x, y=y))
				x = coordlist[0]
				y = coordlist[3]
				keypoints.append(ia.Keypoint(x=x, y=y))
				x = coordlist[2]
				y = coordlist[1]
				keypoints.append(ia.Keypoint(x=x, y=y))
		if (gbldebug): print('objclassprocessed',objclassprocessed)
		
		keypoints_on_images.append(ia.KeypointsOnImage(keypoints, shape=image.shape))

		for i in range(0,numImgGen):
			images.append(image)
			keypoints_on_images.append(ia.KeypointsOnImage(keypoints, shape=image.shape))

		seq = iaa.Sequential([iaa.GaussianBlur((0, 3.0)), iaa.Affine(scale=(0.9, 1.1), rotate=(-1,0))])
		#seq = iaa.Sequential([iaa.GaussianBlur((0, 3.0)), iaa.Grayscale(alpha=(0.0, 1.0)), iaa.Dropout((0.01, 0.1), per_channel=0.5), iaa.Affine(scale=(0.95, 1.05), rotate=(-10,10))])
		seq_det = seq.to_deterministic()
		
		# augment keypoints and images
		#images_aug = seq_det.augment_images([image])
		images_aug = seq_det.augment_images(images)
		keypoints_aug = seq_det.augment_keypoints(keypoints_on_images)
		#print("keypoints_aug",keypoints_aug)
		
		gblmodifiedkeypoints = {}
		gblidx = 1 
		# Example code to show each image and print the new keypoints coordinates
		for img_idx, (image_after, keypoints_after) in enumerate(zip(images_aug, keypoints_aug)):
			image_after_name = str(img_idx)+'_'+imgname
			image_after_path = os.path.join(destdir, image_after_name)
			cv2.imwrite(image_after_path, image_after)
			modifiedrect = []
			modifiedkeypoints = {}
			idx = 1 
			cntr = 1
			for kp_idx, keypoint in enumerate(keypoints_after.keypoints):
				x_new, y_new = keypoint.x, keypoint.y
				
				if (gbldebug): print("new keypoints", x_new, y_new)
				modifiedrect.append([int(x_new), int(y_new)])
				cntr += 1
				if (cntr > 4):
					gblmodifiedkeypoints[gblidx] =modifiedrect
					modifiedkeypoints[idx] = modifiedrect
					if (gbldebug): print(modifiedrect)
					modifiedrect = []
					cntr =1
					idx += 1
					gblidx += 1 
				
				
			if (gbldebug): print('modkey ',modifiedkeypoints)
			objclassidx = 0
			for key, modkey in modifiedkeypoints.items():
				if (gbldebug): print(key,modkey)
				newimgrect = getImgRect(image_after_path,modkey)
				if (gbldebug): print(newimgrect)
				if(newimgrect[0] != '' and newimgrect[1] != '' and newimgrect[2] != '' and newimgrect[3] != ''):
					anno_after_name = str(img_idx)+'_'+annoname
					anno_after_path = os.path.join(destdir, anno_after_name)
					shutil.copy2(annofilepath, anno_after_path)
					if os.path.isfile (anno_after_path):
						#print('key',key,len(objclassprocessed),int(key)-1)
						#print('modu',2%2)
						objclassidex = int(objclassidx) % len(objclassprocessed)
						if (gbldebug): print('objclassidx',objclassidex,objclassidx)
						objclass = objclassprocessed[objclassidex]
						if (gbldebug): print('objclass',objclass)
						setnewannofileupdate = setAnnoCoord(anno_after_path,objclass,newimgrect)
						objclassidx += 1
						if (setnewannofileupdate == False) :
							print("error in processing the annotation file ", anno_after_path)
							break
					else :
						print("error in creating xml file for the path ",anno_after_path)
						break
				else :
		        		print("Error while accessing the co-ordinates of augumented image, kindly check annotation of file ",imgpath)
			#break #for debug to make a single doc run

	except Exception as e:
		print("error occured in getting augumented images")
		print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
		print(e)
		

def getImgRect(imgfilepath,coordlist):
	xmin = ymin = xmax = ymax = ''
	try:
		img = cv2.imread(imgfilepath)
		vrx = np.array(coordlist, np.int32)
		vrx = vrx.reshape((-1,1,2))
		#img = cv2.polylines(img, [vrx], True, (0,255,255),3)
		# get the min area rect
		#rect = cv2.minAreaRect(vrx)
		#box = cv2.boxPoints(rect)
		# convert all coordinates floating point values to int
		#box = np.int0(box)
		# draw a red 'nghien' rectangle
		#cv2.drawContours(img, [box], 0, (0, 0, 255),2)
		#cv2.drawContours(img, [vrx], 0, (0, 0, 255),2)
		# get the bounding rect
		#x, y, w, h = cv2.boundingRect(box)
		x, y, w, h = cv2.boundingRect(vrx)
		#print("x, y, w, h",x, y, w, h)
		# draw a green rectangle to visualize the bounding rect
		cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
		if (gbldebug): cv2.imshow('Draw01',img)
		if (gbldebug): cv2.waitKey(0)
		xmin = x
		ymin = y
		xmax = x+w
		ymax = y+h
	except Exception as e:
		print("error occured in getting augumented images")
		print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
		print(e)

	return([xmin, ymin, xmax, ymax])

def generateAugmented(origin, labels, destination):
	objclasslist = labels
	directory = origin
	destdir = destination
	filepaths = [os.path.join(origin, f) for f in os.listdir(origin)]
	for filepath in filepaths:
		print("file", filepath)
		_, imgfilename = os.path.split(filepath)
		filesplit = imgfilename.split(".")
		if filesplit[len(filesplit)-1] in supportedfiles: 
			annofilename = ''
			annofilename = imgfilename
			annofilename = annofilename.replace(str("."+filesplit[len(filesplit)-1]),'.xml')
			origimgfilepath = os.path.join(directory, imgfilename)
			annofilepath = os.path.join(directory, annofilename)
			print("annofilepath", annofilepath, "origfilepath", origimgfilepath)
			coorddict = getAnnoCoord(annofilepath,objclasslist)
			dataAugment(origimgfilepath,annofilepath,coorddict,destdir)

if __name__ == "__main__":
	try:
		for file in os.listdir(directory):
		    imgfilename = os.fsdecode(file)
		    debug = False
		    if imgfilename.endswith(".jpg"): 
		        annofilename = ''
		        annofilename = imgfilename
		        annofilename = annofilename.replace('.jpg','.xml')
		        origimgfilepath = os.path.join(directory, imgfilename)
		        annofilepath = os.path.join(directory, annofilename)
		        coorddict = getAnnoCoord(annofilepath,objclasslist)
		        if (gbldebug): print(coorddict)
		        dataAugment(origimgfilepath,annofilepath,coorddict,destdir)

	except Exception as e:
		print("error occured in main function")
		print ('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
		print(e)
