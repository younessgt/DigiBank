""" initialize the models package
the db and rd attribute will be loaded from this file"""

from models.engine.Mongodb import Mongodb
from models.engine.Redis import RedisClient

db = Mongodb()
rd = RedisClient()
