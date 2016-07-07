# -*- coding: utf-8 -*- 
from pymongo import MongoClient
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class User:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self._db = client.test_database

    def add_user(self,username, password, mail, roles):
        user = {'name':username, 'password':password, 'mail': mail, 'roles':roles}
        users = self._db.users
        users.insert_one(user)

    def get_user(self, username):
        return self._db.users.find_one({'name':username})

    def get_all_users(self):
        return self._db.users.find()



if __name__ == '__main__':
    user = User()
    roles = ['user']
    #user.add_user('另一个用户','222222', roles)
    users = user.get_all_users()
    for user in users:
        print user['name']
    #print db.get_user('1')
