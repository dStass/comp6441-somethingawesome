from flask import Flask, render_template
from flask_assets import Bundle, Environment

 
app = Flask(__name__)

site_state = {
    'pages': ['home', 'account'],
    'current_page' : 'home'
}

@app.route('/')
def index():
    site_state['current_page'] = 'home'
    return render_template('index.html', site=site_state)

@app.route('/account')
def about():
    site_state['current_page'] = 'account'
    return render_template('account.html', site=site_state)


@app.after_request
def apply_caching(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

# FLASK_APP=application.py FLASK_DEBUG=1 TEMPLATES_AUTO_RELOAD=True python3 -m flask run
if __name__ == '__main__':
    app.run()