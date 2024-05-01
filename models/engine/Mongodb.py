''' Mongodb model'''
import bcrypt
from mongoengine import connect
from pymongo.errors import ConnectionFailure
from models.user import User
from datetime import datetime


class Mongodb():
    ''' Mongodb Class to Manipulate the db'''

    def __init__(self):
        ''' constructor '''
        self.db = 'bank'
        try:
            self.connection = connect(
                self.db, host=f'mongodb://localhost/{self.db}')
            self.connection.admin.command('ping')
            print('Successfully connected')
        except ConnectionFailure as e:
            print(f'Failed to connect: {e}')
            raise ConnectionFailure('Could Not Connect') from e
        
        
    def user_exist(self, email, username):
        """ checking if the email or username already exist """
        
        user_exist_by_email = User.objects(email=email).first()

        user_exist_by_username = User.objects(username=username).first()

        if user_exist_by_email:
            print('email exist')
            return 'email_exist'

        if user_exist_by_username:
            print('username exist')
            return 'username_exist'
        return None

    def create_user(self, email, password, username, currency):
        ''' adding user in db '''

        # user_exist_by_email = User.objects(email=email).first()

        # user_exist_by_username = User.objects(username=username).first()

        # if user_exist_by_email:
        #     print('email exist')
        #     return 'email_exist'

        # if user_exist_by_username:
        #     print('username exist')
        #     return 'username_exist'

        # encrypting password

        # convert password to bytes
        passwrd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(passwrd_bytes, salt)

        info = {
            'email': email.lower(),
            'hashed_password': hashed_password,
            'username': username,
            'currency': currency
        }

        user = User(info)
        user.account['balance'] = 1000
        user.account['status'] = 'active'
        path_image = '/profiles/default/img-default.png'
        user.profile_image_path = path_image

        try:

            user.save()
        except Exception as e:
            print(f"Error saving user: {e}")
        
        return user

    def delete_user(self, email, password):
        ''' deleting user from db and changing status account to inactive '''

        user = User.objects(email=email).first()

        if not user:
            print('No such User')
            return None

        user_dict = user.to_mongo().to_dict()

        hashedpassw = user_dict.get('hashed_password')
        hashedpassw_byte = hashedpassw.encode('utf-8')
        password_bytes = password.encode('utf-8')

        if bcrypt.checkpw(password_bytes, hashedpassw_byte):
            user.account['status'] = 'inactive'
            user.save()
            return user.account['status']
        else:
            return 'noMatch'

    def get_user(self, email):
        ''' retrieve user from db '''

        user = User.objects(email=email).first()

        if not user:
            print('No user')
            return None

        return user

    def update_user_balance(self, user_email,
                            receiver_email, user_amount, receiver_amount):
        ''' updating the user and the receiver account balance '''

        user = self.get_user(user_email)
        receiver = self.get_user(receiver_email)

        if not user:
            print('User Not Found')
            return None

        if not receiver:
            print('Receiver Not Found')
            return None

        user.account['balance'] -= user_amount
        receiver.account['balance'] += receiver_amount

        user.save()
        receiver.save()

    def update_mouvement_transfer(self, user_email,
                                  receiver_email,
                                  user_amount, receiver_amount):
        ''' updation the movement when a user make a transfer'''

        user = self.get_user(user_email)
        receiver = self.get_user(receiver_email)

        if not user or not receiver:

            return None

        withdrawal_mov = {'type': 'withdrawal', 'amount': -
                          user_amount, 'receiver': receiver_email,
                          'date': datetime.now()}
        deposit_mov = {'type': 'deposit', 'amount': receiver_amount,
                       'sender': user_email, 'date': datetime.now()}

        try:
            user.movements.insert(0, withdrawal_mov)
            receiver.movements.insert(0, deposit_mov)
            user.save()
            receiver.save()
            self.update_user_balance(
                user_email, receiver_email, user_amount, receiver_amount)
            withdrawal_mov['date'] = withdrawal_mov['date'].isoformat() + 'Z'
            return withdrawal_mov
        except Exception as e:
            return {'error': e}

    def update_mouvement_loan(self, user_email, amount):
        ''' * handling the loan process
            * mean a deposit on user account'''
        user = self.get_user(user_email)

        if not user:
            return None

        deposit_mov = {'type': 'deposit', 'amount': amount,
                       'sender': 'DigiBank', 'date': datetime.now()}

        try:
            user.movements.insert(0, deposit_mov)
            user.account['balance'] += amount
            user.save()
            deposit_mov['date'] = deposit_mov['date'].isoformat() + 'Z'
            return deposit_mov
        except Exception as e:
            return {'error': e}

    def get_movements(self, user_id):
        ''' getting just the first 10 movements '''

        user = User.objects(id=user_id).only('movements').first()

        if not user:
            return None

        first_10_mov = user.movements[:10]

        if len(first_10_mov) == 0:
            return []

        return first_10_mov

    def get_info_account(self, user_id):
        """ getting a precise user info

        """

        user_v1 = User.objects(id=user_id).only('username').first()
        user_v2 = User.objects(id=user_id).only('account').first()
        user_v3 = User.objects(id=user_id).only('currency').first()
        user_v4 = User.objects(id=user_id).only('profile_image_path').first()

        if not user_v1 or not user_v2 or not user_v3:
            return None

        first_10_mov = self.get_movements(user_id)

        return {
            'username': user_v1.username,
            'currency': user_v3.currency,
            'account': user_v2.account,
            'movements': first_10_mov,
            'profile_img_path': user_v4.profile_image_path
        }

    def check_user(self, email, password):
        ''' checking user crendential when he want to login in '''
        user = User.objects(email=email).first()

        if not user:
            return None

        user_dict = user.to_mongo().to_dict()

        hashedpassw = user_dict.get('hashed_password')
        hashedpassw_byte = hashedpassw.encode('utf-8')
        password_bytes = password.encode('utf-8')

        if bcrypt.checkpw(password_bytes, hashedpassw_byte):
            return user
        else:
            return None

    def update_email(self, email, new_email):
        ''' Updating user email'''
        
        user = User.objects(email=email).first()
        
        if not user:
            return None
        
        user.email = new_email.lower()
        user.save()
        return user
    
    def update_username(self, email, new_username):
        ''' Updating user username'''
        
        user = User.objects(email=email).first()
        
        if not user:
            return None
        
        user.username = new_username
        user.save()
        return user
    
    def update_password(self, email, old_password, new_password):
        ''' Updating user password'''
        
        user = self.check_user(email, old_password)
        print(user)
        
        if not user:
            return None
        
        password_bytes = new_password.encode('utf-8')
        salt = bcrypt.gensalt()
        updated_hashed_password = bcrypt.hashpw(password_bytes, salt)
        user.hashed_password = updated_hashed_password.decode('utf-8')
        
        # print(old_password)
        # print(new_password)
        # print(password_bytes)
        # print(updated_hashed_password)
        # print(updated_hashed_password.decode('utf-8'))
        user.save()
        return user
    
    
    def update_profile_img(self, email, profile_img_path_db):
        '''updating user profile image'''
        
        user = User.objects(email=email).first()
        
        if not user:
            return None
        
        user.profile_image_path = profile_img_path_db
        user.save()
        return user