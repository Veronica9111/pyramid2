# -*- coding: utf-8 -*-
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from time import gmtime, strftime

import sys
reload(sys)
sys.setdefaultencoding('utf8')

class Record:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self._db = client.test_database

    def add_record(self, set_name, set_id, owner, progress, user):
        time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        self._db.insert_one({'set_name': set_name, 'set_id': set_id, 'updated_time': time, 'owner': owner, 'progress': progress, 'user': user})
    def get_all_records(self):
        return self._db.records.find()

    def get_all_records_by_user(self, user_name):
        return self._db.records.find({'user': user_name})

    def get_record_by_id(self, id):
        record = self._db.records.find_one({'_id': ObjectId(id)})
        return record

    def update_record_by_id(self, id, items, passed):
        self._db.records.update({'_id': ObjectId(id)}, {'$set': {'items': items, 'passed': passed}})

    def get_record_by_set_id(self, set_id):
        return self._db.records.find({'set_id': ObjectId(set_id)}).sort('updated_time', pymongo.DESCENDING)
