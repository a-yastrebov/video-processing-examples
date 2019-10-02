'''
Получение кадров с youtube
Требуется pafy: https://pythonhosted.org/Pafy/
'''

import cv2
import pafy

url = "https://www.youtube.com/watch?v=2iVSEvahwj8"
video = pafy.new(url)
best = video.getbest(preftype="mp4")

stream = cv2.VideoCapture(best.url)
while True:
    r,frame = stream.read()
    if frame is None:
        continue
    
    cv2.imshow('video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break        

stream.release()
cv2.destroyAllWindows()