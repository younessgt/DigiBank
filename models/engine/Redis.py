''' Redis model '''

import redis


class RedisClient:
    '''redis class responsible for the communication with the db'''
    def __init__(self):
        '''constructor method'''
        self._client = redis.Redis(host='localhost',
                                   port=6379, db=0, decode_responses=True)

    def get(self, key):
        ''' method to retreive the data'''

        return self._client.get(key)

    def set(self, key, value, duration=None):
        ''' method for storing a key value with duration if neccessary'''

        if value is None:
            raise ValueError("Value cannot be None")
        self._client.set(key, value, ex=duration)

    def incr(self, key, amount=1):
        ''' method to increment the value of a key by a given amount'''

        return self._client.incr(key, amount)

    def del_key(self, key):
        ''' method to delete the data'''
        self._client.delete(key)
