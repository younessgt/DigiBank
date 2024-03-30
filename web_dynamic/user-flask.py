from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import uuid
from models import db, rd
from flask_login import login_user, LoginManager, logout_user, login_required, current_user
from models.user import User
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
# app.secret_key = os.urandom(24)
app.secret_key = 'youp'
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)



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
        return jsonify({'success': False, 'message': 'Account is desactivated'})
    else:

        return jsonify({'success': False, 'message': 'Invalid username or password'})


@app.route('/logout')
@login_required
def logout():
    ''' user logout method'''
    logout_user()
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
        return jsonify({'success': False, 'message': 'Passwords do not match!'})

    msg = db.create_user(email, password, username, currency)

    if msg == 'email_exist':
        return jsonify({'success': False, 'message': 'Email already exists'})
    if msg == 'username_exist':
        return jsonify({'success': False, 'message': 'Username already exists'})

    return jsonify({'success': True})

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


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
