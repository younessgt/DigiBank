""" User model"""

from datetime import datetime
from mongoengine import (
    Document,
    StringField,
    EmailField,
    ListField,
    DictField,
    DateTimeField,
)


class User(Document):
    """User class to define a schema for the user """

    email = EmailField(required=True, unique=True)
    username = StringField(required=True, unique=True)
    currency = StringField(required=True)
    hashed_password = StringField(required=True)
    movements = ListField(DictField())
    account = DictField()
    created_at = DateTimeField(default=datetime.now)

    meta = {'collection': 'users'}

    def __init__(self, data_dict=None, **kwargs):
        if data_dict is not None:
            # Unpack dictionary values into keyword arguments
            kwargs.update(data_dict)
        super().__init__(**kwargs)
