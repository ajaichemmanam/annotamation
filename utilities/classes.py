class labelItem:
    def __init__(self, label, xmin, ymin, xmax, ymax):
        self.label = label
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax


def returnObject(label, xmin, ymin, xmax, ymax):
    o = labelItem(label, xmin, ymin, xmax, ymax)
    return o


class fileProperties:
    def __init__(self, filename, folder, path, imageWidth, imageHeight, imageChannels, size):
        self.filename = filename
        self.folder = folder
        self.path = path
        self.imageWidth = imageWidth
        self.imageHeight = imageHeight
        self.imageChannels = imageChannels
        self.size = size
