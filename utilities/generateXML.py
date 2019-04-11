import xml.etree.cElementTree as ET


def generateXMl(fileProps, objectList):
    annotation = ET.Element("annotation")
    ET.SubElement(annotation, "folder").text = fileProps.folder
    ET.SubElement(annotation, "filename").text = fileProps.filename
    ET.SubElement(annotation, "path").text = fileProps.path

    source = ET.SubElement(annotation, "source")
    ET.SubElement(source, "database").text = "Unknown"

    size = ET.SubElement(annotation, "size")
    ET.SubElement(size, "width").text = str(fileProps.imageWidth)
    ET.SubElement(size, "height").text = str(fileProps.imageHeight)
    ET.SubElement(size, "depth").text = "3"

    ET.SubElement(annotation, "segmented").text = "0"

    for objectItem in objectList:
        objectElement = ET.SubElement(annotation, "object")
        ET.SubElement(objectElement, "name").text = objectItem.label
        ET.SubElement(objectElement, "pose").text = "Unspecified"
        ET.SubElement(objectElement, "truncated").text = "1"
        ET.SubElement(objectElement, "difficult").text = "0"
        bndbox = ET.SubElement(objectElement, "bndbox")
        ET.SubElement(bndbox, "xmin").text = str(
            objectItem.xmin * fileProps.imageWidth)
        ET.SubElement(bndbox, "ymin").text = str(
            objectItem.ymin * fileProps.imageHeight)
        ET.SubElement(bndbox, "xmax").text = str(
            objectItem.xmax * fileProps.imageWidth)
        ET.SubElement(bndbox, "ymax").text = str(
            objectItem.ymax * fileProps.imageHeight)
    tree = ET.ElementTree(annotation)
    filesplit = fileProps.filename.split('.')
    tree.write(fileProps.folder+"\\"+filesplit[0]+".xml")
