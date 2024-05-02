import os
from flask import jsonify, request, g, session, render_template, make_response
from models import db, rd
from flask_login import current_user, login_required
from models.user import User
from api.v1.views import app_views
from functools import wraps
from pathlib import Path
from datetime import datetime, timedelta
from weasyprint import HTML


def request_made(token):
    ''' method that check for number of request'''

    limit_key = f'limit_{token}'
    number_request = rd.get(limit_key)
    if number_request and int(number_request) >= 10:
        return False

    if not number_request and token is not None:
        rd.set(limit_key, 1)
    if number_request and token is not None:
        rd.incr(limit_key)
    return True


def token_or_login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not request_made(token):

            return jsonify({"error": "Request limit reached"}), 429

        key = f'auth_{token}'
        user_token = rd.get(key)
        if token == user_token:
            user_id = rd.get(f"token_to_user_{token}")
            g.user_id = user_id
            return f(*args, **kwargs)
        return jsonify({"error": "Unauthorized"}), 401
    return wrapper


@app_views.route('/some/infos', methods=['GET'], strict_slashes=False)
def get_some_user_infos():
    ''' retreving 10 last user movements ans some additional infos'''

    if not current_user.is_authenticated:
        return jsonify({"error: Unauthorized"}), 401

    user_id = current_user.id
    infos = db.get_info_account(user_id)

    if infos is None:
        return jsonify({'error': "Unauthorized"}), 401

    if len(infos.get('movements', [])) != 0:
        formatted_movements = [
            {**mov, 'date': mov['date'].isoformat() + 'Z'}
            for mov in infos['movements']
        ]

        infos['movements'] = formatted_movements
    return jsonify(infos)


@app_views.route('/transfer', methods=['POST'], strict_slashes=False)
def transfer_funds():
    ''' transferring funds from user account to another account'''

    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401

    user_email = current_user.email
    receiver_email = request.form.get('receiver-email').lower()

    if user_email == receiver_email:
        return jsonify({'success': False, 'user': True}), 401

    user_amount = int(request.form.get('amount'))

    receiver = db.get_user(receiver_email)

    user_currency = current_user.currency

    if not receiver:
        return jsonify({'success': False, 'user': False}), 401

    receiver_currency = receiver.currency

    receiver_amount = user_amount

    if user_currency == 'USD' and receiver_currency == 'EUR':
        receiver_amount = round(user_amount * 0.9, 2)

    if user_currency == 'EUR' and receiver_currency == 'USD':
        receiver_amount = user_amount * 1.09

    status_mov = db.update_mouvement_transfer(
        user_email, receiver_email, user_amount, receiver_amount)

    return jsonify(status_mov), 200


@app_views.route('/loan', methods=['POST'], strict_slashes=False)
def loan():
    ''' processing the loan '''

    if not current_user.is_authenticated:
        return jsonify({'error': "Unauthorized"}), 401

    email = current_user.email
    amount = int(request.form.get('amount'))

    loan_mov = db.update_mouvement_loan(email, amount)

    if 'error' in loan_mov:
        return jsonify({'error': loan_mov['error']}), 400

    return jsonify(loan_mov), 200


@app_views.route('/delete', methods=['POST'], strict_slashes=False)
def delete():
    ''' deleting user by setting his status to inactive'''

    if not current_user.is_authenticated:
        return jsonify({'error': "Unauthorized"}), 401

    user_email = current_user.email
    email = request.form.get('user-email').lower()
    password = request.form.get('password')

    if user_email != email:
        return jsonify({'success': False}), 401

    account_status = db.delete_user(email, password)

    if account_status is None:
        return jsonify({'success': False}), 401

    return jsonify(account_status), 200


@app_views.route('/all/movements', methods=['GET'], strict_slashes=False)
@token_or_login_required
def all_movement():
    ''' retreiving all user mouvements'''
    user_id = getattr(g, 'user_id', None)
    if user_id is None:
        return jsonify({'error': "Unauthorized"}), 401
    user = User.objects(id=user_id).first()
    movements = user.movements
    username = user.username
    id_usr = str(user.id)
    obj = {'username': username, 'id': id_usr, 'movements': movements}
    return jsonify(obj), 200


@app_views.route('/infos', methods=['GET'], strict_slashes=False)
@token_or_login_required
def get_user_infos():
    ''' retreving a user movements '''
    user_id = getattr(g, 'user_id', None)

    if user_id is None:
        return jsonify({'error': "Unauthorized"}), 401

    infos = db.get_info_account(user_id)

    if infos is None:
        return jsonify({'error': "Unauthorized"}), 401

    if len(infos.get('movements', [])) != 0:
        formatted_movements = [
            {**mov, 'date': mov['date'].isoformat() + 'Z'}
            for mov in infos['movements']
        ]

        infos['movements'] = formatted_movements
    return jsonify(infos)


@app_views.route('/update-profile', methods=['POST'], strict_slashes=False)
# @login_required
def update_profile():
    ''' updating user infos '''
    
    username = request.form.get('username')
    new_email = request.form.get('email')
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    file = request.files.get('profile_image')
    
    email = current_user.email
    if username:
        user = db.update_username(email, username)
        if not user:
            return jsonify({'success': False}), 400

    if new_email:
        user = db.update_username(email, new_email)
        if not user:
            return jsonify({'success': False}), 400
        
    if old_password and new_password:
        user = db.update_password(email, old_password, new_password)
        if not user:
            return jsonify({'success': False}), 400
    
    if file:
        try:
            filename = f'img-{current_user.id}'
            current_dir = Path(__file__).resolve().parent
            base_dir = current_dir.parents[2]
            # print('base_dir: ', base_dir)
            path = os.path.join(base_dir, 'profiles', str(current_user.id))
            file_path = os.path.join(path, filename)
            
        
            
    
            os.makedirs(path, exist_ok=True)
            file.save(file_path)
        except PermissionError as e:
            print(f"Permission error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            
        profile_img_path_db = f'/profiles/{current_user.id}/{filename}'
        
        user = db.update_profile_img(email, profile_img_path_db)
        if not user:
            return jsonify({'success': False}), 400

    return jsonify({'success': True}), 200


@app_views.route('/check-movements-date', methods=['POST'], strict_slashes=False)
@login_required
def check_movements_date():
    ''' checking if the dates exists in the db '''
    try:
        data = request.get_json()
        
        if data is None:
            return jsonify({'error': 'No data provided'}), 400
        
        # print(type(data.get('start_date')))
        # print(type(data.get('end_date')))
        
        start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d')+ timedelta(days=1)
        
        print(start_date)
        print(type(start_date))
        
        user = User.objects(id=current_user.id).first()
        # user = User.objects(email='test1@gmail.com').first()
        if user is None:
            return jsonify({'success': False}), 400
        
        filtered_movements = [
            movement for movement in user.movements 
            if 'date' in movement and start_date <= movement['date'].replace(tzinfo=None) <= end_date
        ]
        
        if len(filtered_movements) == 0:
            return jsonify({'success': True, 'movements': False})
        
        print(len(filtered_movements))
        
        for movement in filtered_movements:
            movement['date'] = movement['date'].strftime('%Y-%m-%d')
            
            if movement['type'] == 'deposit':
                movement['receiver'] = current_user.username
            elif movement['type'] == 'withdrawal':
                movement['sender'] = current_user.username
        
        print(filtered_movements)
        session['filtered_movements'] = filtered_movements
        return jsonify({'success': True, 'movements': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    
@app_views.route('/download-statement-pdf', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def download_bank_statement():
    ''' generation a bank statement pdf for user request'''
    
    filtered_movements = session['filtered_movements']
    data = request.get_json()
    if data is None:
            return jsonify({'error': 'No data provided'}), 400
        
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    info = {
        'start_date': start_date,
        'end_date': end_date,
        'username': current_user.username,
        'id': current_user.id,
        'currency': current_user.currency
    }
    
    print(filtered_movements)
    
    if len(filtered_movements) > 0:
        rendered_html = render_template('bank-statement.html', info=info, filtered_movements=filtered_movements)
        # Generate PDF from HTML
        pdf = HTML(string=rendered_html).write_pdf()

        response = make_response(pdf)
        response.headers['Content-Disposition'] = 'attachment; filename=bank_statement.pdf'
        response.headers['Content-Type'] = 'application/pdf'

        return response
        
    return jsonify({'success': True})