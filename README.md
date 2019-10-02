# video-processing-examples
Простые примеры обработки видео на Python.
* video_connection: Получение кадров из различных источников с помощью OpenCV
* opencv_people_detection: Простой детектор людей из OpenCV на классических алгоритмах
* yolo_v3_object_detection: Детектор различных объектов с помощью нейросети YOLOv3

Простейший способ всё запустить:
1) Установить Anaconda (https://www.anaconda.com/distribution/)
2) Если что-то не работает (python, conda, pip), добавить в переменную PATH пути к папкам <Anaconda>, <Anaconda>\scripts, <Anaconda>\Library\bin,
где <Anaconda> путь установки, выбранный в инсталляторе.
3) Установить OpenCV:
    conda install opencv
4) Установить Keras:
    conda install keras
5) Если есть подходящая видеокарта (NVidia with Cuda capability >= 3.5), утсановить tensorflow для GPU:
    conda install tensorflow-gpu
6) Можно запускать примеры.