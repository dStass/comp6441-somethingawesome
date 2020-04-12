import json
import face_recognition as frec
from global_variables import *

def load(json_path):
  f = open(json_path, 'r')
  enrolled = json.loads(f.read())
  for user_id in enrolled[USERS]:
    user_profile = enrolled[PROFILE][user_id]
    image_path = user_profile[PATH]
    for i, image_file in enumerate(user_profile[ENROLLED_IMAGES]):
      image = frec.load_image_file(image_path+image_file)
      image_encoding = frec.face_encodings(image)[0]
      user_profile[ENROLLED_IMAGES][i] = image_encoding  # get replace the file with its encoding

  return enrolled
  

  # print('pass2')
  # users = json_read[USERS]
  # for user in users:
  #   name = user[NAME]
  #   path = user[PATH]
  #   print(name, path)

  # print("loading")
