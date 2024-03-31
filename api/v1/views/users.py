from flask import jsonify, request, g
from models import db, rd
from flask_login import current_user
from models.user import User
from api.v1.views import app_views
from functools import wraps


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