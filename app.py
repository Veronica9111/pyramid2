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
        delete_btn = "<input id='%s' class='delete-quiz btn btn-danger' type='button' value='删除' />" % quiz['_id']
        if type == 'datatable':
            data.append([quiz['name'], quiz['updated_time'], test_btn, edit_btn, delete_btn])
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
        user_name = 'from session'
        quiz_db.add_quiz(name, itemList, user_name, time)
        print 'post'
    elif method == 'UPDATE':
        name = request.params['name']
        items = request.params['items'].split(',')
        itemList = []
        for i in range(0, len(items), 2):
            itemList.append({'question': items[i], 'answer': items[i+1]})
        time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        id = request.params['id']
        quiz_db.update_quiz(id, itemList, name, time)
        print 'update'
    elif method == 'DELETE':
        print 'delete'
    return json.dumps({'status': 'ok', 'data': data}, encoding="UTF-8", ensure_ascii=False)

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
    config.add_route('quiz', '/quiz/{id}')
    config.add_route('operate_set', '/set')
    config.add_route('get_all_sets', '/sets')
    config.add_route('test', '/test/{id}')
    config.add_route('index', '')
    config.add_static_view(name='static', path='/Users/veronica/Documents/pyramid2/static')
    config.add_view(hello_world, route_name='hello')
    config.add_view(index, route_name='index', renderer='__main__:templates/index.pt')
    config.add_view(first, route_name='first', renderer='__main__:templates/first.pt')
    config.add_view(manage, route_name='manage', renderer='__main__:templates/manage.pt')
    config.add_view(show, route_name='show', renderer='__main__:templates/show.pt')
    config.add_view(test, route_name='test', renderer='__main__:templates/test.pt')
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
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
