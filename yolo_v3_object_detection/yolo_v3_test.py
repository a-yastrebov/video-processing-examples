''' 
based on https://github.com/experiencor/keras-yolo3
Детектирование объектов различных классов с помощью нейросети YOLO v3 (https://pjreddie.com/darknet/yolo/)
Желательно наличие GPU
Готовую модель (h5) нужно взять здесь: https://drive.google.com/file/d/1_FD5Lk76cX95v025yk3OcxuEDPfrUEFR/view?usp=sharing
'''
import cv2
import numpy as np
from numpy import expand_dims
from keras.models import load_model
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from matplotlib import pyplot
from matplotlib.patches import Rectangle
 
class BoundBox:
	def __init__(self, xmin, ymin, xmax, ymax, objness = None, classes = None):
		self.xmin = xmin
		self.ymin = ymin
		self.xmax = xmax
		self.ymax = ymax
		self.objness = objness
		self.classes = classes
		self.label = -1
		self.score = -1
 
	def get_label(self):
		if self.label == -1:
			self.label = np.argmax(self.classes)
 
		return self.label
 
	def get_score(self):
		if self.score == -1:
			self.score = self.classes[self.get_label()]
 
		return self.score
 
def _sigmoid(x):
	return 1. / (1. + np.exp(-x))
 
def decode_netout(netout, anchors, obj_thresh, net_h, net_w):
    # Парсим выход YOLO v3
	grid_h, grid_w = netout.shape[:2]
	nb_box = 3
	netout = netout.reshape((grid_h, grid_w, nb_box, -1))
	nb_class = netout.shape[-1] - 5
	boxes = []
	netout[..., :2]  = _sigmoid(netout[..., :2])
	netout[..., 4:]  = _sigmoid(netout[..., 4:])
	netout[..., 5:]  = netout[..., 4][..., np.newaxis] * netout[..., 5:]
	netout[..., 5:] *= netout[..., 5:] > obj_thresh
 
	for i in range(grid_h*grid_w):
		row = i / grid_w
		col = i % grid_w
		for b in range(nb_box):
			# 4-ый элемент - вероятность того, что это фон
			objectness = netout[int(row)][int(col)][b][4]
			if(objectness.all() <= obj_thresh): continue
			# первые 4 элемента - x, y, w, и h
			x, y, w, h = netout[int(row)][int(col)][b][:4]
			x = (col + x) / grid_w
			y = (row + y) / grid_h
			w = anchors[2 * b + 0] * np.exp(w) / net_w
			h = anchors[2 * b + 1] * np.exp(h) / net_h
			# остальные элементы - вероятности принадлежности к одному из классов
			classes = netout[int(row)][col][b][5:]
			box = BoundBox(x-w/2, y-h/2, x+w/2, y+h/2, objectness, classes)
			boxes.append(box)
	return boxes
 
def correct_yolo_boxes(boxes, image_h, image_w, net_h, net_w):
	new_w, new_h = net_w, net_h
	for i in range(len(boxes)):
		x_offset, x_scale = (net_w - new_w)/2./net_w, float(new_w)/net_w
		y_offset, y_scale = (net_h - new_h)/2./net_h, float(new_h)/net_h
		boxes[i].xmin = int((boxes[i].xmin - x_offset) / x_scale * image_w)
		boxes[i].xmax = int((boxes[i].xmax - x_offset) / x_scale * image_w)
		boxes[i].ymin = int((boxes[i].ymin - y_offset) / y_scale * image_h)
		boxes[i].ymax = int((boxes[i].ymax - y_offset) / y_scale * image_h)
 
def _interval_overlap(interval_a, interval_b):
	x1, x2 = interval_a
	x3, x4 = interval_b
	if x3 < x1:
		if x4 < x1:
			return 0
		else:
			return min(x2,x4) - x1
	else:
		if x2 < x3:
			 return 0
		else:
			return min(x2,x4) - x3
 
def bbox_iou(box1, box2):
	intersect_w = _interval_overlap([box1.xmin, box1.xmax], [box2.xmin, box2.xmax])
	intersect_h = _interval_overlap([box1.ymin, box1.ymax], [box2.ymin, box2.ymax])
	intersect = intersect_w * intersect_h
	w1, h1 = box1.xmax-box1.xmin, box1.ymax-box1.ymin
	w2, h2 = box2.xmax-box2.xmin, box2.ymax-box2.ymin
	union = w1*h1 + w2*h2 - intersect
	return float(intersect) / union
 
def do_nms(boxes, nms_thresh):
	if len(boxes) > 0:
		nb_class = len(boxes[0].classes)
	else:
		return
	for c in range(nb_class):
		sorted_indices = np.argsort([-box.classes[c] for box in boxes])
		for i in range(len(sorted_indices)):
			index_i = sorted_indices[i]
			if boxes[index_i].classes[c] == 0: continue
			for j in range(i+1, len(sorted_indices)):
				index_j = sorted_indices[j]
				if bbox_iou(boxes[index_i], boxes[index_j]) >= nms_thresh:
					boxes[index_j].classes[c] = 0
 
def prepare_frame(frame, shape):
    h,w,c = frame.shape
    pframe = cv2.resize(frame, shape)
    pframe = cv2.cvtColor(pframe,cv2.COLOR_BGR2RGB)
    pframe = pframe.astype(float)/255
    pframe = np.expand_dims(pframe, axis=0)
    return pframe, w, h	
 
# получим все предсказания, превышающие заданный порог
def get_boxes(boxes, labels, thresh):
	v_boxes, v_labels, v_scores = list(), list(), list()
	
	for box in boxes:		
		for i in range(len(labels)):			
			if box.classes[i] > thresh:
				v_boxes.append(box)
				v_labels.append(labels[i])
				v_scores.append(box.classes[i]*100)
				# не прерываем: одна ячейка может предсказать несколько классов
	return v_boxes, v_labels, v_scores
 

# загружаем модель
model = load_model('yolo_v3_model.h5')
# определим размер входного изображения для модели
input_w, input_h = 416, 416

# открываем видеоролик
cap = cv2.VideoCapture('../data/test.mp4')

while(True):
    # Читаем по одному кадру, пока ролик не закончится
    ret, frame = cap.read()
    
    frame = cv2.resize(frame, (640, 480))
    image, image_w, image_h = prepare_frame(frame, (input_w, input_h))
    # выполняем детектирование объектов на кадре
    yhat = model.predict(image)

    print([a.shape for a in yhat])
    # определим анкоры
    anchors = [[116,90, 156,198, 373,326], [30,61, 62,45, 59,119], [10,13, 16,30, 33,23]]
    # порог уверенности для вывода детектируемого объекта
    class_threshold = 0.6
    boxes = list()
    for i in range(len(yhat)):	    
	    boxes += decode_netout(yhat[i][0], anchors[i], class_threshold, input_h, input_w)
    
    correct_yolo_boxes(boxes, image_h, image_w, input_h, input_w)
    # используем Non-maximum supression для убирания лишних срабатываний на одни и те же объекты
    do_nms(boxes, 0.5)
    # определим метки классов
    labels = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck",
	    "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
	    "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe",
	    "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard",
	    "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard",
	    "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana",
	    "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake",
	    "chair", "sofa", "pottedplant", "bed", "diningtable", "toilet", "tvmonitor", "laptop", "mouse",
	    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator",
	    "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"]
    
    v_boxes, v_labels, v_scores = get_boxes(boxes, labels, class_threshold)
    
    for i in range(len(v_boxes)):
        print(v_labels[i], v_scores[i])
    
	# рисуем боксы и выводим названия классов
    for i in range(len(v_boxes)):
        box = v_boxes[i]        
        y1, x1, y2, x2 = box.ymin, box.xmin, box.ymax, box.xmax
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, v_labels[i], (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0),2)
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
cv2.waitKey(1)