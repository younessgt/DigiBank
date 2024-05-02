import os
import uuid
import random
import string
from flask import (
    Flask,
    render_template,
    request, redirect,
    url_for,
    jsonify,
    session,
    send_from_directory,
    g
)
from models import db, rd
from flask_login import (
    login_user,
    LoginManager,
    logout_user,
    login_required,
    current_user
)
from models.user import User
from flask_wtf.csrf import CSRFProtect
from flask_oauthlib.client import OAuth
from dotenv import load_dotenv
from flask_mail import Mail, Message
# from flask_cors import CORS

load_dotenv()
app = Flask(__name__)


app.secret_key = os.environ.get('FLASK_SECRET_KEY')
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "noreplayapp8@gmail.com"
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
# CORS(app)

# OAuth Configuration
oauth = OAuth(app)

google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
google_client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')

google = oauth.remote_app(
    'google',
    consumer_key=google_client_id,
    consumer_secret=google_client_secret,
    request_token_params={
        'scope': 'email profile'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)


@login_manager.user_loader
def load_user(user_id):
    """ callback used to reload the user
    object from the user ID stored in the session """

    return User.objects(id=user_id).first()


@app.route('/', strict_slashes=False)
def home():
    ''' home page'''
    return render_template('home.html')


@app.route('/app')
@login_required
def page_app():
    ''' rendering  app page '''
    return render_template('app.html')


@app.route('/login', methods=['POST'], strict_slashes=False)
def login():
    ''' handling user Authentication '''
    email = request.form.get('email')
    password = request.form.get('password')

    if email:
        email = email.lower()

    user = db.check_user(email, password)
    if user and user.account['status'] == 'active':
        login_user(user)
        return jsonify({'success': True})

    elif user and user.account['status'] == 'inactive':
        return jsonify({'success': False,
                        'message': 'Account is desactivated'})
    else:

        return jsonify({'success': False,
                        'message': 'Invalid username or password'})


@app.route('/logout')
@login_required
def logout():
    ''' user logout method'''
    logout_user()
    session.clear()
    return redirect(url_for('home'))


@app.route('/signup', methods=['POST'], strict_slashes=False)
def signup():
    '''creating a new user'''
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    re_password = request.form.get('re-password')
    currency = request.form.get('currency')
    
    

    if password != re_password:
        return jsonify({'success': False,
                        'message': 'Passwords do not match!'})

    # msg = db.create_user(email, password, username, currency)
    msg = db.user_exist(email, username)

    if msg == 'email_exist':
        return jsonify({'success': False, 'message': 'Email already exists'})
    if msg == 'username_exist':
        return jsonify({'success': False,
                        'message': 'Username already exists'})


    # generating verification code
    key = f'email_verification_{email}'
    email_verification_code = rd.get(key)
    
    if email_verification_code:
        rd.del_key(key)
        
    email_verification_code = "".join(random.choice('0123456789') for _ in range(4))
    rd.set(key, email_verification_code, 300)
    
    # storing user info in flask session to use it on multiple requests
    # "use case in /verification route"
    session['user_info'] = {
        'email': email,
        'username': username,
        'password': password,
        'currency': currency
    }
    
    print("email_verification_code: ", email_verification_code )
    # sending email Part
    email_msg_title = "Email Verification"
    sender = "noreplay@digibank.com"
    email_msg = Message(email_msg_title, sender=sender, recipients=[email])
    email_msg.body = ""
    data = {
        'username': username,
        'verification_code': int(email_verification_code)
    }
    email_msg.html = render_template('verification-email.html', data=data)
    
    try:
        mail.send(email_msg)
        # print('Email send Successfully')
    except Exception as e:
        print(e)
    return jsonify({'success': True})


@app.route('/verification', methods=['POST'], strict_slashes=False)
def verification_code_signup():
    ''' verify the sign up verification code'''
    user_info = session['user_info']
    email = user_info.get('email')
    username = user_info.get('username')
    password = user_info.get('password')
    currency = user_info.get('currency')
    
    try:
        data = request.get_json()
        # print(data)
        if data is None:
            return jsonify({'error': 'No data provided'}), 400
        verification_code = data.get('code')
        if not verification_code:
            return jsonify({'error': 'Verification code is required'}), 400

        # print("Received verification code:", verification_code)
        
        key = f'email_verification_{email}'
        email_verification_code = rd.get(key)
        
        
        if email_verification_code is None:

            return jsonify({"success": False, 'status': "expired"})

        if email_verification_code != verification_code:

            return jsonify({"success": False, 'status': "not match"})
        
        if email_verification_code == verification_code:

            try:

                db.create_user(email, password, username, currency)
                return jsonify({'success': True}), 200
            except Exception as e:
                return jsonify({'error': str(e)}), 500
 
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/token', methods=['GET'], strict_slashes=False)
def token():
    ''' returning a token if the current user doesn't owns one yet'''
    if not current_user.is_authenticated:
        return jsonify({'error': 'User not authenticated.'}), 401
    user_id = current_user.id
    key = f'user_{user_id}'

    user_token = rd.get(key)
    if user_token is None:
        user_token = str(uuid.uuid4())
        rd.set(key, user_token, 36000)
        rd.set(f'auth_{user_token}', user_token, 36000)
        rd.set(f"token_to_user_{user_token}", str(user_id), 36000)
    return jsonify({'token': user_token}), 200


@app.route('/google-login')
def google_login():
    """Initiates the Google OAuth authentication flow"""
    return google.authorize(
        callback=url_for('google_authorized', _external=True))


# /callback is setup in google cloud in Authorized redirect
# URIs 'http://127.0.0.1:5000/callback'
@app.route('/callback')
def google_authorized():
    """Handles the callback from Google OAuth
    after the user grants authorization"""
    resp = google.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return jsonify({
            'success': False,
            'message': 'Access denied: reason=%s error=%s' % (
                request.args['error_reason'],
                request.args['error_description']
            )
        })

    session['google_token'] = (resp['access_token'], '')
    user_info = google.get('userinfo')
    user_email = user_info.data['email']

    user = db.get_user(user_email)
    if user is None:
        characters = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(characters) for _ in range(12))
        username = user_info.data['name']
        user = db.create_user(user_email, password, username, 'EUR')

    login_user(user)
    return redirect(url_for('home'))


@google.tokengetter
def get_google_oauth_token():
    """ Retrieves the OAuth token associated with
    the current user for Google OAuth provider from
    flask session.
    """
    
    return session.get('google_token')

@app.route('/user')
def user_profile():
    return render_template('user-profile.html')


@app.route('/profiles/<path:filename>')
def custom_static(filename):
    return send_from_directory('../profiles', filename)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
