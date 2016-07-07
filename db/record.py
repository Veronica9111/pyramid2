# -*- coding: utf-8 -*-
from pymongo import MongoClient
from bson.objectid import ObjectId

import sys
reload(sys)
sys.setdefaultencoding('utf8')

class Record:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self._db = client.test_database

    def get_all_records(self):
        return self._db.records.find()

    def get_all_records_by_user(self, user_name):
        return self._db.records.find({'user': user_name})

    def get_record_by_id(self, id):
        record = self._db.records.find_one({'_id': ObjectId(id)})
        return record
