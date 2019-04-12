class objectItem:
    def __init__(self, label, xmin, ymin, xmax, ymax):
        self.label = label
        self.xmin = xmin
        self.ymin = ymin
        self.xmax = xmax
        self.ymax = ymax


class fileProperties:
    def __init__(self, filename, path, imageWidth, imageHeight, imageChannels, size):
        self.filename = filename
        self.path = path
        self.imageWidth = imageWidth
        self.imageHeight = imageHeight
        self.imageChannels = imageChannels
        self.size = size
