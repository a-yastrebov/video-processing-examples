'''
Детектирование людей методами классического компьютерного зрения с помощью OpenCV
Based on https://www.pyimagesearch.com/2015/11/09/pedestrian-detection-opencv/
'''
import numpy as np
import cv2
 
# Инициализируем вычислитель признаков объекта, использующий HOG (гистограммы ориентированных градиентов)
hog = cv2.HOGDescriptor()
# Инициализируем обученный SVM-классификатор для распознавания людей
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
cv2.startWindowThread()

# Открываем ролик для чтения кадров
cap = cv2.VideoCapture('../data/test.mp4')
# Открываем ролик для записи
out = cv2.VideoWriter(
    'output.avi',
    cv2.VideoWriter_fourcc(*'MJPG'),
    15.,
    (640,480))
while(True):
    # Читаем по одному кадру, пока ролик не закончится
    ret, frame = cap.read()
    frame = cv2.resize(frame, (640, 480))
    # Данный классификатор работает на монохромных изображениях - преобразуем в оттенки серого
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    # Вызываем детектор, получаем список боксов и уверенностей
    boxes, weights = hog.detectMultiScale(frame, winStride=(8,8) )
    boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])
    for (xA, yA, xB, yB) in boxes:
        cv2.rectangle(frame, (xA, yA), (xB, yB),
                          (0, 255, 0), 2)
    
    out.write(frame.astype('uint8'))
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
cv2.waitKey(1)