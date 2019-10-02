'''
Получение кадров с web-камеры
'''
import cv2

stream = cv2.VideoCapture(0)
while True:
    r,frame = stream.read()
    if frame is None:
        continue
    
    cv2.imshow('video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break        

stream.release()
cv2.destroyAllWindows()