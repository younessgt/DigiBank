from models.engine.Mongodb import Mongodb
from models import db, rd
from models.user import User
import asyncio

# db.create_user('test1@gmail.com', 'helloworld123', 'User1', 'USD')
# db.create_user('test2@gmail.com', 'helloworld124', 'User2', 'EUR')
# db.create_user('test3@gmail.com', 'helloworld14', 'User3', 'EUR')


# db.delete_user('test1@gmail.com', 'helloworld123')
# user = db.get_user('test1@gmail.com')

# user.account['status'] = 'active'

# user.save()

# user = db.update_email('profile1@gmail.com', 'updatedprofile1@gmail.com')
user = db.update_username('updatedprofile1@gmail.com', 'updatedprofile1')

# db.update_mouvement_loan('test1@gmail.com', 900)
# db.update_mouvement_loan('test2@gmail.com', 900)
# db.update_mouvement_transfer('test1@gmail.com', 'test2@gmail.com', 100


# db.update_mouvement_transfer('test2@gmail.com', 'test1@gmail.com', 20, 25)
# db.update_mouvement_transfer('test1@gmail.com', 'test2@gmail.com', 30, 24)
# db.update_mouvement_transfer('test1@gmail.com', 'test2@gmail.com', 40, 35)
# db.update_mouvement_transfer('test2@gmail.com', 'test1@gmail.com', 50, 55)
# db.update_mouvement_transfer('test2@gmail.com', 'test1@gmail.com', 10, 15)
# db.update_mouvement_transfer('test1@gmail.com', 'test3@gmail.com', 120, 110)
# db.update_mouvement_transfer('test3@gmail.com', 'test1@gmail.com', 140, 120)
# db.update_mouvement_transfer('test2@gmail.com', 'test1@gmail.com', 25, 30)
# db.update_mouvement_transfer('test2@gmail.com', 'test1@gmail.com', 42, 50)
# db.update_mouvement_transfer('test3@gmail.com', 'test1@gmail.com', 220, 210)


# db.get_movements('test1@gmail.com')

# db.get_info_account('test1@gmail.com')

# # db.create_user('test3@gmail.com', 'hellowrld124', 'User3', 'france')
# db.get_movements('test2@gmail.com')


# for user in User.objects(movements__match={'reciever': {'$exists': True}}):
#     updated_movements = []
#     for movement in user.movements:
#         if 'reciever' in movement:
#             # Rename 'reciever' to 'receiver'
#             movement['receiver'] = movement.pop('reciever')
#         updated_movements.append(movement)
#     user.movements = updated_movements  # Update the user's movements
#     user.save()  # Save the updated user document



### redis
# async def test_redis_operations():
#     await rd.set('user_id', '123')

# asyncio.run(test_redis_operations())