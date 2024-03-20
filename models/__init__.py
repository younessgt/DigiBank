""" initialize the models package
the db attribute will be loaded from this file"""

from models.engine.Mongodb import Mongodb

db = Mongodb()
