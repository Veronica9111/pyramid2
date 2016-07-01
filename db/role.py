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

    def add_role(self, name, permissions):
        role = {'name': name, 'permissions': permissions}
        roles = self._db.roles
        result = roles.insert(role)
        return result

    def get_role_by_id(self, id):
        role = self._db.roles.find_one({'_id': ObjectId(id)})
        return role

    def add_permission_to_role(self, roleId, permissionId, checked):
        role = self.get_role_by_id(roleId)
        permissions = role['permissions']
        if checked == 'true':
            permissions.append(permissionId)
        else:
            permissions.remove(permissionId)
        self._db.roles.update({'_id': ObjectId(roleId)}, {'$set': {'permissions': permissions}}, False, True)

    def delete_role(self):
        print ""

    def get_all_roles(self):
        return self._db.roles.find()
