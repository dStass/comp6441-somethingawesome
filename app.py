# from-imports
import time

# imports
import cv2
import numpy as np
# import matplotlib.pyplot as plt


from load import load
from compare import compare
from global_variables import *

# cv2
CASCADE_PATH = cv2.data.haarcascades
CASCADE = "haarcascade_frontalface_default.xml"
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(CASCADE_PATH + CASCADE)

# json
JSON_PATH = 'data/'
JSON_FILE = 'userbase.json'
stored = load(JSON_PATH+JSON_FILE)

# time
SLEEP_PERIOD = 1
NAME_PERIOD = 0.5
last_checked = time.time()

# name
name_overlay = [None, 0]
BUFFER = 10
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SIZE = 1
FONT_COLOUR = (255, 0, 0)
LINE_TYPE = 2


while True:
  ret, frame = cap.read()
  grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
  faces_detected = face_cascade.detectMultiScale(grey_frame, 1.3, 5)  # numbers differ on resolution and image quality, etc
  
  # draw the frame

  # detect and draw a rectangle around user's face
  for (x, y, w, h) in faces_detected:
    new_time = time.time()
    cv2.rectangle(frame, (x, y), (x+w, y+h), (255,0,0), 2)

    # draw name
    if name_overlay[0]:
      print(x,y)
      cv2.putText(frame, name_overlay[0], (x, y - BUFFER), FONT, FONT_SIZE, FONT_COLOUR, LINE_TYPE)
      if time.time() - name_overlay[1] > NAME_PERIOD:
        name_overlay[0] = None

    if new_time - last_checked > SLEEP_PERIOD:
      last_checked = new_time
      returned_id = compare(frame, stored)
      if returned_id:
        returned_name = stored[PROFILE][returned_id][NAME]
        name_overlay = [returned_name, time.time()]
        print("DETECTED:" + returned_name)

    # only check for one face
    break
  cv2.imshow('frame', frame)
    

  # print(len(frame))

  # if user presses 'q', we stop the application
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

# out.release()
cap.release()
cv2.destroyAllWindows()