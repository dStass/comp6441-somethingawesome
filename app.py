# imports
import time
import cv2
import numpy as np
import webbrowser

# flask
from flask import Flask, render_template
from flask_assets import Bundle, Environment


# local
from load import load
from compare import compare
from global_variables import *




# json
JSON_PATH = 'data/'
JSON_FILE = 'userbase.json'
stored = load(JSON_PATH+JSON_FILE)


# time
SLEEP_PERIOD = 1
NAME_PERIOD = 1


# name
BUFFER = 10  # px
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SIZE = 1
FONT_COLOUR = (255, 0, 0)
LINE_TYPE = 2



# CAMERA STUFF
def start_camera():
  # cv2
  CASCADE_PATH = cv2.data.haarcascades
  CASCADE = "haarcascade_frontalface_default.xml"
  cap = cv2.VideoCapture(0)
  face_cascade = cv2.CascadeClassifier(CASCADE_PATH + CASCADE)

  last_checked = time.time()
  name_overlay = [None, 0]
  page_opened = False
  while True:
    # if page_opened:
    #   break

    ret, frame = cap.read()
    grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces_detected = face_cascade.detectMultiScale(grey_frame, 1.3, 5)  # numbers differ on resolution and image quality, etc
    
    # draw the frame

    # detect and draw a rectangle around user's face
    for (x, y, w, h) in faces_detected:
      new_time = time.time()
      cv2.rectangle(frame, (x, y), (x+w, y+h), FONT_COLOUR, 2)

      # draw name
      if name_overlay[0]:
        cv2.putText(frame, name_overlay[0], (x, y - BUFFER), FONT, FONT_SIZE, FONT_COLOUR, LINE_TYPE)
        if time.time() - name_overlay[1] > NAME_PERIOD:
          name_overlay[0] = None

      if new_time - last_checked > SLEEP_PERIOD:
        last_checked = new_time
        returned_id = compare(frame, stored)
        if returned_id:
          cap.release()
          cv2.destroyAllWindows()
          return returned_id
          # returned_name = stored[PROFILE][returned_id][NAME]
          # name_overlay = [returned_name, time.time()]

          # webbrowser.open('https://www.donaldjtrump.com/')
          # print("DETECTED:" + returned_name)
          # page_opened = True
          # break

      # only check for one face
      break
    cv2.imshow('frame', frame)
      

    # if user presses 'q', we stop the application
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  # out.release()
  cap.release()
  cv2.destroyAllWindows()



# flask
app = Flask(__name__)

site_state = {
  'pages': ['home', 'login'],
  'current_page' : 'home'
}

@app.route('/')
def index():
  site_state['current_page'] = 'home'
  return render_template('index.html', site=site_state)

@app.route('/login')
def account():
  site_state['current_page'] = 'login'
  returned_id = start_camera()
  name = stored[PROFILE][returned_id][NAME]
  fun_fact = stored[PROFILE][returned_id][FUN_FACT]
  static_file = 'images/' + str(returned_id) + '.jpg'

  site_state['NAME'] = name
  site_state['FUN_FACT'] = fun_fact
  site_state['PROFILE_PICTURE'] = static_file

  return render_template('account.html', site=site_state)


@app.after_request
def apply_caching(response):
  response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
  return response

# FLASK_APP=application.py FLASK_DEBUG=1 TEMPLATES_AUTO_RELOAD=True python3 -m flask run
app.run()
print('test')
