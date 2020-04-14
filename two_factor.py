import yagmail
import random
from datetime import datetime
from load import load_simple

AUTH_CODE_SIZE = 6

def generate_auth(size = AUTH_CODE_SIZE):
  to_return = ''
  for _ in range(size):
    to_return += str(random.randint(0,9))
  return to_return

def send_single(to_name, to_email, auth_code = None):
  send_multi(to_name, [to_email], auth_code)

def send_multi(to_name, to_emails, auth_code = None):
  CREDENTIALS_PATH = 'credentials.json'
  credentials = load_simple(CREDENTIALS_PATH)
  from_user = credentials['yagmail']['email']
  from_password = credentials['yagmail']['password']

  sent_from = from_user
  to = to_emails
  subject = 'Two factor authentication'
  body = auth_code
  if not body:
    body = generate_auth()

  email_text = """
  Hi {},

  Your two factor authentication code is:
  {}

  Time of this sign in request:
  {}
  """.format(to_name, body, str(datetime.now()))

  try:
    yagmail_handle = yagmail.SMTP(from_user, from_password)
    for t in to:
        yagmail_handle.send(t, subject, email_text)

    print('Email sent!')
  except:
    print('Failed to send email')


# send_single("David", "dstiasny@outlook.com", random_digits())