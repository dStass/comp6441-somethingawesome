import face_recognition as frec
from global_variables import *

def compare(candidate, enrolled):
  candidate_encoding_raw = frec.face_encodings(candidate)
  if len(candidate_encoding_raw) == 0:
    return None
  candidate_encoding = candidate_encoding_raw[0]

  # go through our stored database
  for user_id in enrolled[USERS]:
    user_profile = enrolled[PROFILE][user_id]
    image_path = user_profile[PATH]
    # for image_encoding in user_profile[ENROLLED_IMAGES]:
    results = frec.compare_faces(user_profile[ENROLLED_IMAGES], candidate_encoding)
    if results[0]:
      return user_id

  return None