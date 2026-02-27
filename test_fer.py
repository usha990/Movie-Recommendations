from fer import FER
import cv2
import tensorflow as tf


detector =FER()
cap=cv2.VideoCapture(0)
while True:
    ret,frame=cap.read()
    emotions=detector.detect_emotions(frame)
    print(emotions)
    cv2.imshow("frame",frame)
    if cv2.waitKey(1) & 0XFF == 27:
        break
        cap.release()
        cv2.destroyAllWindows()