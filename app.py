# imports
import time
import cv2
import numpy as np
import hashlib

import webbrowser

# flask
from flask import Flask, render_template, request, session
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
NAME_PERIOD = 1
SLEEP_PERIOD = 1

# name
BUFFER = 10  # px
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SIZE = 1
BLUE = (255, 0, 0)  # B G R for some reason
RED = (0, 0, 255)
LINE_TYPE = 2



# CAMERA STUFF
def start_camera():
  # cv2
  CASCADE_PATH = cv2.data.haarcascades
  CASCADE = "haarcascade_frontalface_default.xml"
  # cv2.namedWindow('Face Detection', cv2.WINDOW_NORMAL)
  cap = cv2.VideoCapture(0)
  face_cascade = cv2.CascadeClassifier(CASCADE_PATH + CASCADE)

  last_checked = time.time()
  name_overlay = [None, None, 0]
  face_found = False
  x, y = 0, 0
  while True:
    ret, frame = cap.read()
    grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces_detected = face_cascade.detectMultiScale(grey_frame, 1.3, 5)  # numbers differ on resolution and image quality, etc
    
    # draw name
    if face_found:
      cv2.putText(frame, 'Confirmed: ' + name_overlay[1], (x, y - BUFFER), FONT, FONT_SIZE, BLUE, LINE_TYPE)
      if time.time() - name_overlay[2] > NAME_PERIOD:
        cap.release()
        cv2.destroyAllWindows()
        return name_overlay[0]

    if len(faces_detected) == 1:
      x,y,w,h = faces_detected[0]
      new_time = time.time()

      # detect and draw a rectangle around user's face
      cv2.rectangle(frame, (x, y), (x+w, y+h), BLUE, 2)
      if not face_found and new_time - last_checked > SLEEP_PERIOD:
        last_checked = new_time
        returned_id = compare(frame, stored)
        if returned_id:
          returned_name = stored[PROFILE][returned_id][NAME]
          name_overlay = [returned_id, returned_name, new_time]
          face_found = True

    elif len(faces_detected) > 1:
      cv2.putText(frame, str(len(faces_detected)) + ' Faces Detected' , (x, y - BUFFER), FONT, FONT_SIZE, RED, LINE_TYPE)
      for (x, y, w, h) in faces_detected:
        cv2.rectangle(frame, (x, y), (x+w, y+h), RED, 2)
      face_found = False


    cv2.imshow('frame', frame)
    cv2.moveWindow('frame', 2000, 200)
      
    # if user presses 'q', we stop the application
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  # out.release()
  cap.release()
  cv2.destroyAllWindows()
  return None



# flask
app = Flask(__name__)
app.secret_key = 'secret_key'

site_state = {
  'pages': ['home', 'login'],
  'current_page' : 'home'
}

@app.route('/')
def index():
  site_state['current_page'] = 'home'
  return render_template('index.html', site=site_state)

@app.route('/login')
def account(auth = False, returned_id = None):
  site_state['current_page'] = 'login'
  site_state['AUTHENTICATED'] = auth
  if not auth:
    returned_id = start_camera()
    if not returned_id:
      return index()
  else:
    name = stored[PROFILE][returned_id][NAME]
    fun_fact = stored[PROFILE][returned_id][FUN_FACT]
    static_file = 'images/' + str(returned_id) + '.jpg'

    site_state['NAME'] = name
    site_state['FUN_FACT'] = fun_fact
    site_state['PROFILE_PICTURE'] = static_file
  
  session['USER_ID'] = returned_id

  return render_template('account.html', site=site_state)

@app.route('/validate', methods=["POST"])
def validate():
  print(request, request.form)
  session_id = session.get('USER_ID', None)
  auth = False
  if session_id:
    if hashlib.sha256(request.form['password'].encode('utf-8')).hexdigest() == stored[PROFILE][session_id][SHA256]:
      auth = True
    else:
      session_id = None
    # auth = True
  return account(auth, session_id)

@app.after_request
def apply_caching(response):
  response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
  return response

# FLASK_APP=application.py FLASK_DEBUG=1 TEMPLATES_AUTO_RELOAD=True python3 -m flask run
app.run(debug=True)
print('test')
