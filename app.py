# imports
import time
import cv2
import numpy as np
import hashlib
import random
import threading
import webbrowser

# flask
from flask import Flask, render_template, request, session
from flask_assets import Bundle, Environment


# local
from load import load
from compare import compare
from global_variables import *
import two_factor


# MS Windows Specific
from win32api import GetSystemMetrics


# json
JSON_PATH = 'data/'
JSON_FILE = 'userbase.json'
stored = load(JSON_PATH + JSON_FILE)


# time
NAME_PERIOD = 3
SLEEP_PERIOD = 0.2


# CV2
WINDOW_FACTOR = 0.4


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
  face_cascade = cv2.CascadeClassifier(CASCADE_PATH + CASCADE)

  cap = cv2.VideoCapture(0)
  ret, frame = cap.read()

  rescale_dimensions = get_rescale_dimensions(frame, WINDOW_FACTOR)
  frame = apply_rescale(frame, rescale_dimensions)

  move_coordinates = get_move_coordinates(frame)



  last_checked = time.time()
  name_overlay = [None, None, 0]
  face_found = False
  x, y = 0, 0
  while True:
    ret, frame = cap.read()
    # frame = apply_rescale(frame, rescale_dimensions)


    grey_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces_detected = face_cascade.detectMultiScale(grey_frame, 1.3, 5)  # numbers differ on resolution and image quality, etc
    # a default

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
      if new_time - last_checked > SLEEP_PERIOD:
        last_checked = new_time
        returned_id = compare(frame, stored)
        
        if returned_id:
          if name_overlay[0] != returned_id:
            returned_name = stored[PROFILE][returned_id][NAME]
            name_overlay = [returned_id, returned_name, new_time]
            face_found = True

    elif len(faces_detected) > 1:
      cv2.putText(frame, str(len(faces_detected)) + ' Faces Detected' , (x, y - BUFFER), FONT, FONT_SIZE, RED, LINE_TYPE)
      for (x, y, w, h) in faces_detected:
        cv2.rectangle(frame, (x, y), (x + w, y + h), RED, 2)
      face_found = False

    cv2.imshow('frame', frame)
    # apply_frame_move('frame', move_coordinates)
      
    # if user presses 'q', we stop the application
    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

  # out.release()
  cap.release()
  cv2.destroyAllWindows()
  return None

def get_rescale_dimensions(frame, factor):
  window_width = int(frame.shape[1])
  window_height = int(frame.shape[0])

  screen_width = GetSystemMetrics(0)
  screen_height = GetSystemMetrics(1)

  factor_width = (screen_width * factor)/window_width
  factor_height = (screen_height * factor)/window_height

  factor = min(factor_width, factor_height)

  window_width = int(window_width * factor)
  window_height = int(window_height * factor)

  return (window_width, window_height)

def apply_rescale(frame, dimensions):
  return cv2.resize(frame, dimensions, interpolation = cv2.INTER_AREA)

def get_move_coordinates(frame):
  window_width = int(frame.shape[1])
  window_height = int(frame.shape[0])

  screen_width = GetSystemMetrics(0)
  screen_height = GetSystemMetrics(1)

  width_difference = screen_width - window_width
  height_difference = screen_height - window_height

  new_x = int(width_difference/2)
  new_y = int(height_difference/2)

  return (new_x, new_y)

def apply_frame_move(frame_name, move_coordinates):
  cv2.moveWindow(frame_name, move_coordinates[0], move_coordinates[1])


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

  site_state['USER_ID'] = returned_id
  session['USER_ID'] = returned_id
  name = stored[PROFILE][returned_id][NAME]
  email = stored[PROFILE][returned_id][EMAIL]

  if not auth:
    # handle authentication code 
    generated_auth = two_factor.generate_auth()
    session['AUTH'] = generated_auth
    two_factor.send_single(name, email, generated_auth)

  else:
    fun_fact = stored[PROFILE][returned_id][FUN_FACT]
    static_file = 'images/' + str(returned_id) + '.jpg'

    site_state['NAME'] = name
    site_state['FUN_FACT'] = fun_fact
    site_state['PROFILE_PICTURE'] = static_file
  
  # send authentication email to user
  return render_template('account.html', site=site_state)

@app.route('/validate', methods=["POST"])
def validate():
  print(request, request.form)
  session_id = session.get('USER_ID', None)
  auth = False

  if session_id:
    verify_password = hashlib.sha256(request.form['PASSWORD'].encode('utf-8')).hexdigest() == stored[PROFILE][session_id][SHA256]
    verify_auth = request.form['AUTH'] == session.get('AUTH', None)
    if verify_password and verify_auth:
      auth = True
    else:
      session_id = None
  return account(auth, session_id)

@app.after_request
def apply_caching(response):
  response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
  return response

port = 5000 + random.randint(0, 999)
url = "http://127.0.0.1:{0}".format(port)

# open website in a different thread
threading.Timer(1.25, lambda: webbrowser.open(url) ).start()
app.run(port=port, debug=False)