# Import ObjectItem Class
from utilities.classes import labelItem

max_boxes_to_draw = 20
min_score_thresh = 0.5


def findObjects(boxes, classes, scores, category_index):
    objectList = []
    for i in range(min(max_boxes_to_draw, boxes.shape[0])):
        if scores is None or scores[i] > min_score_thresh:
            ymin, xmin, ymax, xmax = tuple(boxes[i].tolist())
            if classes[i] in category_index.keys():
                label = category_index[classes[i]]['name']
            else:
                label = 'N/A'
            o = labelItem(label, xmin, ymin, xmax, ymax)
            objectList.append(o)
    return objectList
