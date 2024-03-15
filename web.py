from flask import Flask, redirect, url_for, session, request
from flask_oauthlib.client import OAuth
import json
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'

oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key='202782780730-au1pe7280jn50nbhpsg0lmedlmk9djpu.apps.googleusercontent.com',
    consumer_secret='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',
    request_token_params={
        'scope': 'https://www.googleapis.com/auth/calendar',
    },
    base_url='https://www.googleapis.com/calendar/v3/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

@app.route('/')
def index():
    if 'google_token' in session:
        return redirect(url_for('calendar'))
    return 'Please <a href="/login">login</a>'

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('index'))

@app.route('/login/authorized')
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    
    session['google_token'] = (response['access_token'], '')
    return redirect(url_for('calendar'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route('/calendar')
def calendar():
    # Use the Google Calendar API here to fetch and display calendar data
    return 'Calendar data goes here'

@app.route('/insert-event', methods=['POST'])
def insert_event():
    if 'google_token' not in session:
        return redirect(url_for('login'))

    access_token = session['google_token'][0]

    event_data = request.json
    event_date = event_data.get('date')
    event_description = event_data.get('description')

    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }

    event = {
        'summary': 'Study Task',
        'description': event_description,
        'start': {
            'dateTime': f'{event_date}T09:00:00',
            'timeZone': 'Your_Time_Zone',
        },
        'end': {
            'dateTime': f'{event_date}T10:00:00',
            'timeZone': 'Your_Time_Zone',
        },
    }

    response = requests.post(
        'https://www.googleapis.com/calendar/v3/calendars/primary/events',
        headers=headers,
        data=json.dumps(event)
    )

    if response.status_code == 200:
        return 'Event inserted successfully!'
    else:
        return f'Error inserting event: {response.text}'

if __name__ == '__main__':
    app.run(debug=True)
