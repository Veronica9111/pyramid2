# -*- coding: utf-8 -*- 
from pymongo import MongoClient
from bson.objectid import ObjectId

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class Permission:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self._db = client.test_database

    def add_permission(self, permission_name):
        permission = {'name': permission_name}
        permissions = self._db.permissions
        id = permissions.insert_one(permission)
        return id

    def get_all_permissions(self):
        return self._db.permissions.find()

    def delete_permission(self, id):
        self._db.permissions.delete_one({'_id': ObjectId(id)})
