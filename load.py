import os
import json
import face_recognition as frec
from global_variables import *

def load(json_path):
  enrolled = load_simple(json_path)
  for user_id in enrolled[USERS]:
    user_profile = enrolled[PROFILE][user_id]
    image_path = user_profile[PATH]
    image_encodings = []

    # for all files in directory
    for image_file in os.listdir(image_path):
      image = frec.load_image_file(image_path + image_file)
      image_encoding = frec.face_encodings(image)[0]
      image_encodings.append(image_encoding)

    user_profile[ENROLLED_IMAGES] = image_encodings
  return enrolled
  
def load_simple(json_path):
  f = open(json_path, 'r')
  read_json = json.loads(f.read())
  return read_json