# -*- coding: utf-8 -*- 
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import json
import shutil
import hashlib
from time import gmtime, strftime

from wsgiref.simple_server import make_server
from pyramid.session import SignedCookieSessionFactory
my_session_factory = SignedCookieSessionFactory('itsaseekreet')
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.renderers import render_to_response
import pyramid.httpexceptions as exc


from db.user import User
from db.permission import Permission
from db.role import Role
from db.quiz import Quiz
from db.record import Record
from quiz import Quiz_Handler

def hello_world(request):
    return Response('Hello %(name)s!' % request.matchdict)

@view_config(route_name='login', renderer='json')
def login(request):
    name = request.params['name']
    password = request.params['password']
    user_db = User()
    user = user_db.get_user(name)
    if user is None:
        return {'status': 'nok', 'data': '该用户不存在！'}
    m = hashlib.md5()
    m.update(password)
    passwordStr = m.hexdigest()
    print passwordStr
    if passwordStr == user['password']:
        print 'before session'
        request.session['name'] = name
        roles = user['roles']
        print 'ok'
        return {'status': 'ok', 'roles': roles}
    else:
        return {'status':'nok', 'data': '密码错误！'}

@view_config(route_name='get_all_users', renderer='string')
def get_all_users(request):
    user_db = User()
    users = user_db.get_all_users()
    data = []
    for user in users:
        print user['name']
        data.append([user['name'], user['password'], ','.join(user['roles'])])
    print data
    str = json.dumps(data, encoding="UTF-8", ensure_ascii=False)
    print str
    return json.dumps({'status': 'ok', 'data': str}, encoding="UTF-8", ensure_ascii=False)

@view_config(route_name='get_all_permissions', renderer='string')
def get_all_permissions(request):
    type = request.params['type']
    permission_db = Permission()
    permissions = permission_db.get_all_permissions()
    data = []
    for permission in permissions:
        delete_button = "<input id='%s' class='delete-permission btn btn-danger' type='button' value='删除'/>" % permission['_id']
        if type == 'datatable':
            data.append([permission['name'],delete_button])
        elif type == 'list':
            data.append({'name': permission['name'], 'id': "%s" % (permission['_id'])})
    print data
    str = json.dumps(data, encoding="UTF-8", ensure_ascii=False)
    return json.dumps({'status': 'ok', 'data': str}, encoding="UTF-8", ensure_ascii=False)

@view_config(route_name='operate_permission', renderer='string')
def operate_permission(request):
    permission_db = Permission()
    method = request.params['method']
    if method == 'GET':
        print "get one permission"
    elif method == 'POST':
        name = request.params['name']
        id = permission_db.add_permission(name)
        delete_btn = "<input id='%s' class='delete-permission btn btn-danger' type='button' value='删除'/>" % id
        data = [name, delete_btn]
        str = json.dumps(data, encoding="UTF-8", ensure_ascii=False)
        return json.dumps({'status': 'ok', 'data': str}, encoding="UTF-8", ensure_ascii=False)
    elif method == 'DELETE':
        permission_id = request.params['id']
        permission_db.delete_permission(permission_id)
        return json.dumps({'status': 'ok'}, encoding="UTF-8", ensure_ascii=False)

@view_config(route_name='get_all_roles', renderer='string')
def get_all_roles(request):
    type = request.params['type']
    role_db = Role()
    roles = role_db.get_all_roles()
    data = []
    for role in roles:
        edit_btn = "<input name='%s' class='edit-role btn btn-primary' type='button' value='编辑'/>" % role['_id']
        delete_btn = "<input id='%s' class='delete-role btn btn-danger' type='button' value='删除' />" % role['_id']
        if type == 'datatable':
            data.append([role['name'],edit_btn, delete_btn])
        elif type == 'list':
            data.append({'name': role['name'], 'id': '%s' % (role['_id']), 'permissions': role['permissions']})
    str = json.dumps(data, encoding="UTF-8", ensure_ascii=False)
    return json.dumps({'status': 'ok', 'data': str}, encoding="UTF-8", ensure_ascii=False)

@view_config(route_name='operate_role', renderer='string')
def operate_role(request):
    role_db = Role()
    method = request.params['method']
    if method == 'GET':
        print 'get one role'
    elif method == 'POST':
        name = request.params['name']
        print request.params
        permissions = request.params['permissions'].split(',')
        id = role_db.add_role(name, permissions)
        data = "%s" % id
        str = json.dumps(data, encoding="UTF-8", ensure_ascii=False)
        return json.dumps({'status': 'ok', 'data': str}, encoding="UTF-8", ensure_ascii=False)
    elif method == 'DELETE':
        
        print 'delete one role'
    elif method == 'UPDATE_ROLE_PERMISSION':
        roleId = request.params['role_id']
        permissionId = request.params['permission_id']
        checked = request.params['checked']
        role_db.add_permission_to_role(roleId, permissionId, checked)

@view_config(route_name='get_all_sets', renderer='string')
def get_all_sets(request):
    type=request.params['type']
    range = ''
    if 'range' in request.params:
        range = request.params['range']
    quiz_db = Quiz()
    if range == 'mine':
        print range
        print request.session['name']
        quizzes = quiz_db.get_all_quizzes_by_user(request.session['name'])
    else:
        quizzes = quiz_db.get_all_quizzes()
    data = []
    for quiz in quizzes:
        test_btn = "<input name='%s' class='test-quiz btn btn-success' type='button' value='测试' />" % quiz['_id']
        edit_btn = "<input name='%s' class='edit-quiz btn btn-primary' type='button' value='编辑' />" % quiz['_id']
        delete_btn = "<input name='%s' class='delete-quiz btn btn-danger' type='button' value='删除' />" % quiz['_id']
        if type == 'datatable':
            data.append([quiz['name'], quiz['updated_time'], test_btn, edit_btn, delete_btn])
        elif type == 'name':
            data.append({'name': quiz['name'], 'id': "%s" % quiz['_id']})
    return json.dumps({'status': 'ok', 'data': data}, encoding="UTF-8", ensure_ascii=False)

@view_config(route_name='get_all_records', renderer='string')
def get_all_records(request):
    type = request.params['type']
    range = ''
    record_db = Record()
    quiz_db = Quiz()
    if 'range' in request.params:
        range = request.params['range']
        if range == 'mine':
            records = record_db.get_all_records_by_user(request.session['name'])
    else:
        records = record_db.get_all_records()
    data = []
    for record in records:
        id = "%s" % record['_id']
        quiz = quiz_db.get_quiz_by_id(id)
        if record['progress'] == '100':
            progress = 'result'
        else:
            progress = record['progress'] + '%'
        progress_btn = "<input name='%s' type='button' class='progress-quiz btn btn-primary' value='%s'/>" % (record['_id'], progress)
        restart_btn = "<input name='%s' type='button' class='restart-quiz btn btn-success' value='Restart' />" % record['_id']
        if type == 'datatable':
            data.append([record['set_name'], record['owner'], record['updated_time'], record['progress'], progress_btn, restart_btn])
    return json.dumps({'status': 'ok', 'data': data}, encoding="UTF-8", ensure_ascii=False)

@view_config(route_name='operate_set', renderer='string')
def operate_set(request):
    method = request.params['method']
    quiz_db = Quiz()
    data = {}
    if method == 'GET':
        id = request.params['id']
        set = quiz_db.get_quiz_by_id(id)
        data['name'] = set['name']
        data['items'] = set['items']
        print 'get'
    elif method == 'POST':
        name = request.params['name']
        items = request.params['items'].split(',')
        itemList = []
        for i in range(0, len(items), 2):
            itemList.append({'question': items[i], 'answer': items[i+1]})
        time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        user_name = request.session['name']
        quiz_db.add_quiz(name, itemList, user_name, time)
        print 'post'
    elif method == 'UPDATE':
        if 'name' in request.params:
            name = request.params['name']
        else:
            name = None
        if 'type' in request.params:
            type = request.params['type']
        else:
            type = None
        id = request.params['id']
        items = request.params['items'].split(',')
        itemList = []
        for i in range( 0, len(items), 2):
            itemList.append({'question': items[i], 'answer': items[i+1]})
        if type == 'append':
            set = quiz_db.get_quiz_by_id(id)
            itemList = set['items'] + itemList
        time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        quiz_db.update_quiz(id, itemList, name, time)
        print 'update'
    elif method == 'DELETE':
        id = request.params['id']
        quiz_db.delete_quiz(id)
    return json.dumps({'status': 'ok', 'data': data}, encoding="UTF-8", ensure_ascii=False)

@view_config(route_name='operate_record', renderer='string')
def operate_record(request):
    method = request.params['method']
    record_db = Record()
    data = []
    result = {}
    if method == 'GET':
        id = request.params['id']
        record = record_db.get_record_by_id(id)
        set_name = record['set_name']
        set_id = record['set_id']
        items = record['items']
        passed = record['passed']
        type = request.params['type']
        if type == 'datatable':
            for item in items:
                cp_btn = "<input question='%s' answer='%s' class='copy-word btn btn-primary' type='button' value='Copy'/>" % (item['question'], item['answer'])
                data.append([item['question'], item['answer'], item['count'], cp_btn])
        result['name'] = set_name
        result['data'] = data
        result['passed'] = passed
        result['set_id'] = "%s" % set_id
    elif method == 'GET_BY_SET':
        set_id = request.params['id']
        records = record_db.get_record_by_set_id(set_id)
        print records
        for record in records:
            result['name'] = record['set_name']
            result['updated_time'] = record['updated_time']
            result['id'] = "%s" % record['_id']
            break
    elif method == 'POST':
        set_id = request.params['set_id']
        quiz_db = Quiz()
        set = quiz_db.get_quiz_by_id(set_id)
        set_name = set['name']
        owner = set['user']
        progress = 0
        user = request.session['name']
        record_db.add_record(set_name, set_id, owner, progress, user)
    elif method == 'UPDATE':
        id = request.params['id']
        question = request.params['question']
        answer = request.params['answer']
        status = request.params['status']
        record = record_db.get_record_by_id(id)
        passed = record['passed']
        if status == 'yes':
            passed.append(question)
        items = record['items']
        hit = False
        for item in items:
            if question == item['question']:
                hit = True
                if status == 'no':
                    item['count'] += 1
                break
        if hit == False:
            if status == 'yes':
                count = 0
            else:
                count = 1
            items.append({'question': question, 'answer': answer, 'count': count})
        record_db.update_record_by_id(id, items, passed)

    return json.dumps({'status': 'ok', 'data': result}, encoding="UTF-8", ensure_ascii=False)

@view_config(route_name='upload_img', renderer='json')
def upload_img(request):
    filename = request.POST['img'].filename
    input_file = request.POST['img'].file
    with open(filename, 'wb') as fd:
        shutil.copyfileobj(input_file, fd)
    return {'status': 'ok'}

@view_config(route_name='upload_quiz', renderer='json')
def upload_quiz(request):
    file = request.POST['0'].file
    qh = Quiz_Handler(file)
    items = qh.get_items()
    return json.dumps({'status': 'ok', 'data': items}, encoding="UTF-8", ensure_ascii=False)

@view_config(route_name='logout', renderer='json')
def logout(request):
    del request.session['name']
    return {'status': 'ok'}

@view_config(route_name='register', renderer='json')
def register(request):
    name = request.params['name']
    mail = request.params['mail']
    password = request.params['password']
    print password
    m = hashlib.md5()
    m.update(password)
    passwordStr = m.hexdigest()
    user_db = User()
    user_db.add_user(name, passwordStr, mail, ['user'])
    return {'status': 'ok'}

@view_config(route_name='check_user', renderer='json')
def check_user(request):
    user_db = User()
    name = request.params['name']
    user = user_db.get_user_by_name(name)
    if user:
        return {'status': 'nok'}
    else:
        return {'status': 'ok'}

@view_config(route_name='check_mail', renderer='json')
def check_mail(request):
    user_db = User()
    mail = request.params['mail']
    user = user_db.get_user_by_mail(mail)
    if user:
        return {'status': 'nok'}
    else:
        return {'status': 'ok'}

@view_config(route_name='authentication', renderer="json")
def authentication(request):
    if 'name' in request.session:
        return {'status': 'ok'}
    else:
        return {'status': 'nok'}

@view_config(renderer='templates/index.pt')
def index(request):
    return {'name': 'hola'}

@view_config(renderer='templates/first.pt')
def first(request):
    name = request.session['name']
    print name
    return {'name':name}

@view_config(renderer='templates/show.pt')
def show(request):
    name = request.session['name']
    return {'name': name}

@view_config(renderer='templates/manage.pt')
def manage(request):
    name = request.session['name']
    return {'name':name}

@view_config(renderer='templates/quizzes.pt')
def quizzes(request):
    return {'name': 'quizzes'}

@view_config(renderer='templates/test.pt')
def test(request):
    if 'id' in request.matchdict:
        return {'name': 'test'}

@view_config(renderer='templates/history.pt')
def history(request):
    return {'name': 'history'}

@view_config(renderer='templates/result.pt')
def result(request):
    return {'name': 'result'}

@view_config(renderer='templates/all.pt')
def all(request):
    return {'name': 'all'}

def quiz(request):
    print request.matchdict
    if 'id' in request.matchdict:
        if request.matchdict['id'] == '0':
            return render_to_response('__main__:templates/quiz.pt',
                                    {'name': 'name'},
                                    request=request)
        else:
            return render_to_response('__main__:templates/editquiz.pt',
                              {'foo':1, 'bar':2},
                              request=request)

if __name__ == '__main__':
    config = Configurator()
    config.set_session_factory(my_session_factory)
    config.include('pyramid_chameleon')
    config.add_route('hello', '/hello/{name}')
    config.add_route('login', '/login')
    config.add_route('first', '/first')
    config.add_route('logout', '/logout')
    config.add_route('manage', '/manage')
    config.add_route('get_all_users', '/users')
    config.add_route('get_all_permissions', '/permissions')
    config.add_route('operate_permission', '/permission')
    config.add_route('get_all_roles', '/roles')
    config.add_route('operate_role', '/role')
    config.add_route('show', '/show')
    config.add_route('upload_img', '/upload_img')
    config.add_route('upload_quiz', '/upload_quiz')
    config.add_route('download_quiz', '/download_quiz')
    config.add_route('quizzes', '/quizzes')
    config.add_route('all', '/all')
    config.add_route('quiz', '/quiz/{id}')
    config.add_route('operate_set', '/set')
    config.add_route('get_all_sets', '/sets')
    config.add_route('test', '/test/{id}')
    config.add_route('history', '/history')
    config.add_route('result', '/result/{id}')
    config.add_route('operate_record', '/record')
    config.add_route('get_all_records', '/records')
    config.add_route('register', '/register')
    config.add_route('check_user', '/checkuser')
    config.add_route('check_mail', '/checkmail')
    config.add_route('index', '')
    config.add_route('authentication', '/authentication')
    config.add_static_view(name='static', path='/Users/veronica/Documents/pyramid2/static')
    config.add_view(hello_world, route_name='hello')
    config.add_view(index, route_name='index', renderer='__main__:templates/index.pt')
    config.add_view(first, route_name='first', renderer='__main__:templates/first.pt')
    config.add_view(manage, route_name='manage', renderer='__main__:templates/manage.pt')
    config.add_view(show, route_name='show', renderer='__main__:templates/show.pt')
    config.add_view(test, route_name='test', renderer='__main__:templates/test.pt')
    config.add_view(history, route_name='history', renderer='__main__:templates/history.pt')
    config.add_view(result, route_name='result', renderer='__main__:templates/result.pt')
    config.add_view(all, route_name='all', renderer='__main__:templates/all.pt')
    config.add_view(login, route_name='login', renderer='json')
    config.add_view(logout, route_name='logout', renderer='json')
    config.add_view(get_all_users, route_name='get_all_users', renderer='string')
    config.add_view(get_all_permissions, route_name='get_all_permissions', renderer='string')
    config.add_view(operate_permission, route_name='operate_permission', renderer='string')
    config.add_view(get_all_roles, route_name='get_all_roles', renderer='string')
    config.add_view(operate_role, route_name='operate_role', renderer='string')
    config.add_view(upload_img, route_name='upload_img', renderer='json')
    config.add_view(upload_quiz, route_name='upload_quiz', renderer='json')
    config.add_view(quiz, route_name='quiz')#, renderer='__main__:templates/quiz.pt')
    config.add_view(quizzes, route_name='quizzes', renderer='__main__:templates/quizzes.pt')
    config.add_view(get_all_sets, route_name='get_all_sets', renderer='string')
    config.add_view(operate_set, route_name='operate_set', renderer='string')
    config.add_view(get_all_records, route_name='get_all_records', renderer='string')
    config.add_view(operate_record, route_name='operate_record', renderer='string')
    config.add_view(register, route_name='register', renderer='json')
    config.add_view(check_user, route_name='check_user', renderer='json')
    config.add_view(check_mail, route_name='check_mail', renderer='json')
    config.add_view(authentication, route_name='authentication', renderer='json')
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
