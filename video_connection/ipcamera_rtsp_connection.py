'''
Получение кадров с IP-камеры по RTSP
'''
import cv2

stream = cv2.VideoCapture('rtsp://admin:admin12345@192.168.100.226')
while True:
    r,frame = stream.read()
    if frame is None:
        continue
    
    cv2.imshow('video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break        

stream.release()
cv2.destroyAllWindows()
