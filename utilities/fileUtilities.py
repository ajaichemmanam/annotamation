import os
import random
import shutil
import sys


def splitTestTrainFiles(path, testDir, trainDir, testPercentage, trainPercentage):
    try:
        supportedfiles = ["jpg", "jpeg", "png", "bmp"]
        lst = sorted(os.listdir(path))
        print("Number of Files to split", len(lst))
        testIdx = 0
        while testIdx < (len(lst) * testPercentage / 100):
            filename = random.choice(os.listdir(path))
            filesplit = filename.split('.')
            if filesplit[len(filesplit)-1] in supportedfiles:
                xmlFilename = filename.replace(
                    str("."+filesplit[len(filesplit)-1]), '.xml')
                if(os.path.isfile(os.path.join(path, filename))) and (os.path.isfile(os.path.join(path, xmlFilename))):
                    shutil.move(os.path.join(path, filename),
                                os.path.join(testDir, filename))
                    shutil.move(os.path.join(path, xmlFilename),
                                os.path.join(testDir, xmlFilename))
                    testIdx += 2
                    # print("testImage", filename)
                    # print("testImageXML", xmlFilename)
        print("Moved {} files to {} folder".format(str(testIdx), testDir))
        for filename in os.listdir(path):
            filesplit = filename.split('.')
            if filesplit[len(filesplit)-1] in supportedfiles:
                xmlFilename = filename.replace(
                    str("."+filesplit[len(filesplit)-1]), '.xml')
                if(os.path.isfile(os.path.join(path, filename))) and (os.path.isfile(os.path.join(path, xmlFilename))):
                    shutil.move(os.path.join(path, filename),
                                os.path.join(trainDir, filename))
                    shutil.move(os.path.join(path, xmlFilename),
                                os.path.join(trainDir, xmlFilename))
                    # print("trainImage", filename)
                    # print("trainImageXML", xmlFilename)
        print("Moved {} files to {} folder".format(
            str(len(lst)-testIdx), trainDir))
        return True
    except Exception as e:
        print("Split Test Train Error" + str(e))
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
        return False
