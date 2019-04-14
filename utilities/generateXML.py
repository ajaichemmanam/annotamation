try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

# Import Classes
from utilities.classes import labelItem, fileProperties

import sys


def generateXML(fileProps, objectList):
    try:
        annotation = ET.Element("annotation")
        ET.SubElement(annotation, "folder").text = fileProps.folder
        ET.SubElement(annotation, "filename").text = fileProps.filename
        ET.SubElement(annotation, "path").text = fileProps.path

        source = ET.SubElement(annotation, "source")
        ET.SubElement(source, "database").text = "Unknown"

        size = ET.SubElement(annotation, "size")
        ET.SubElement(size, "width").text = str(fileProps.imageWidth)
        ET.SubElement(size, "height").text = str(fileProps.imageHeight)
        ET.SubElement(size, "depth").text = str(fileProps.imageChannels)

        ET.SubElement(annotation, "segmented").text = "0"

        for labelItem in objectList:
            objectElement = ET.SubElement(annotation, "object")
            ET.SubElement(objectElement, "name").text = labelItem.label
            ET.SubElement(objectElement, "pose").text = "Unspecified"
            ET.SubElement(objectElement, "truncated").text = "1"
            ET.SubElement(objectElement, "difficult").text = "0"
            bndbox = ET.SubElement(objectElement, "bndbox")
            ET.SubElement(bndbox, "xmin").text = str(
                int(labelItem.xmin * fileProps.imageWidth))
            ET.SubElement(bndbox, "ymin").text = str(
                int(labelItem.ymin * fileProps.imageHeight))
            ET.SubElement(bndbox, "xmax").text = str(
                int(labelItem.xmax * fileProps.imageWidth))
            ET.SubElement(bndbox, "ymax").text = str(
                int(labelItem.ymax * fileProps.imageHeight))
        tree = ET.ElementTree(annotation)
        filesplit = fileProps.filename.split('.')
        tree.write(fileProps.folder+"\\"+filesplit[0]+".xml")
    except Exception as e:
        print("Error in Generating XML: "+str(e))
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))


def getAnnotaitonXML(xmlpath):
    label = ''
    objectList = []
    fileProps = fileProperties("", "", "", "", "", "", "")
    try:
        tree = ET.ElementTree(file=xmlpath)
        root = tree.getroot()
        for elem in root.iter():
            if elem.tag == 'folder':
                fileProps.folder = elem.text

            elif elem.tag == 'filename':
                fileProps.filename = elem.text

            elif elem.tag == 'path':
                fileProps.path = elem.text
            elif elem.tag == 'size':
                fileProps.imageWidth = elem[0].text
                fileProps.imageWidth = elem[1].text
                fileProps.imageChannels = elem[2].text
            elif elem.tag == 'object':
                for subelem in elem:
                    if subelem.tag == "name":
                        label = subelem.text
                    elif subelem.tag == "bndbox":
                        o = labelItem(
                            label, subelem[0].text, subelem[1].text, subelem[2].text, subelem[3].text)
                        objectList.append(o)
    except Exception as e:
        print("Error in getting annotation from XML: "+str(e))
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
    return fileProps, objectList


def setAugAnnotationXML(fileProps, objectList):
    try:
        annotation = ET.Element("annotation")
        ET.SubElement(annotation, "folder").text = fileProps.folder
        ET.SubElement(annotation, "filename").text = fileProps.filename
        ET.SubElement(annotation, "path").text = fileProps.path

        source = ET.SubElement(annotation, "source")
        ET.SubElement(source, "database").text = "Unknown"

        size = ET.SubElement(annotation, "size")
        ET.SubElement(size, "width").text = str(fileProps.imageWidth)
        ET.SubElement(size, "height").text = str(fileProps.imageHeight)
        ET.SubElement(size, "depth").text = str(fileProps.imageChannels)

        ET.SubElement(annotation, "segmented").text = "0"

        for labelItem in objectList:
            objectElement = ET.SubElement(annotation, "object")
            ET.SubElement(objectElement, "name").text = labelItem.label
            ET.SubElement(objectElement, "pose").text = "Unspecified"
            ET.SubElement(objectElement, "truncated").text = "1"
            ET.SubElement(objectElement, "difficult").text = "0"
            bndbox = ET.SubElement(objectElement, "bndbox")
            ET.SubElement(bndbox, "xmin").text = str(
                labelItem.xmin)
            ET.SubElement(bndbox, "ymin").text = str(
                labelItem.ymin)
            ET.SubElement(bndbox, "xmax").text = str(
                labelItem.xmax)
            ET.SubElement(bndbox, "ymax").text = str(
                labelItem.ymax)
        tree = ET.ElementTree(annotation)
        filesplit = fileProps.filename.split('.')
        tree.write(fileProps.folder+"\\"+filesplit[0]+".xml")
    except Exception as e:
        print("Error in Setting Aug Annotation: "+str(e))
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
