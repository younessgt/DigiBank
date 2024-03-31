import unittest
from datetime import datetime
from mongoengine import connect, disconnect
from mongoengine.errors import NotUniqueError, ValidationError
import mongomock
from models.user import User


class UserTestCase(unittest.TestCase):
    ''' class for testing user model'''
    @classmethod
    def setUpClass(cls):
        connect('banktest', host='localhost',
                mongo_client_class=mongomock.MongoClient)

    @classmethod
    def tearDownClass(cls):
        disconnect()

    def setUp(self):
        User.objects.delete()

    def test_create_user(self):
        user = User(
            email='test@example.com',
            username='testuser',
            hashed_password='hashedpassword123',
            country='Testland',
            movements=[{'type': 'deposit', 'time': datetime.now()}],
            account={'status': 'active'}
        )
        user.save()
        self.assertIsNotNone(user.id)
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.country, 'Testland')
        self.assertEqual(user.account['status'], 'active')
        self.assertTrue(isinstance(user.movements, list))

    def test_email_uniqueness(self):
        User(email='test1@example.com', username='user1',
             hashed_password='pass1').save()

        with self.assertRaises(NotUniqueError):
            User(email='test1@example.com', username='user2',
                 hashed_password='pass2').save()

    def test_required_fields(self):
        with self.assertRaises(ValidationError):
            User(email='test3@example.com',
                 username='user3').save()

    def test_default_created_at(self):
        user = User(
            email='test4@example.com',
            username='user4',
            hashed_password='pass4'
        )
        user.save()

        self.assertTrue(isinstance(user.created_at, datetime))
