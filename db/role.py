# -*- coding: utf-8 -*-
from pymongo import MongoClient
from bson.objectid import ObjectId

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class Role:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self._db = client.test_database

    def add_role(self, name):
        role = {'name': name}
        roles = self._db.roles
        result = roles.insert(role)
        return result

    def add_permission_to_role(self):
        print ""

    def delete_role(self):
        print ""

    def get_all_roles(self):
        return self._db.roles.find()
