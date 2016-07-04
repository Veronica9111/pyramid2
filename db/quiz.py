# -*- coding: utf-8 -*-
from pymongo import MongoClient
from bson.objectid import ObjectId

import sys
reload(sys)
sys.setdefaultencoding('utf8')

class Quiz:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self._db = client.test_database

    def add_quiz(self, quiz_name, quiz_items, user_name, time):
        quizzes = self._db.quizzes
        quiz = {'name':quiz_name, 'items': quiz_items, 'user': user_name, 'created_time': time, 'updated_time': time}
        id = quizzes.insert_one(quiz)
        return id

    def update_quiz(self, objectId, quiz_items):
        self._db.quizzes.update({'_id': ObjectId(objectId)}, {'$set':{'items': quiz_items}}, False, True)

    def get_all_quizzes(self):
        return self._db.quizzes.find()

    def get_quiz_by_id(self, id):
        quiz = self._db.quizzes.find_one({'_id': ObjectId(id)})
        return quiz
