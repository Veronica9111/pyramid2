# -*- coding: utf-8 -*- 
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import json

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

def hello_world(request):
    return Response('Hello %(name)s!' % request.matchdict)

@view_config(route_name='login', renderer='json')
def login(request):
    name = request.params['name']
    password = request.params['password']
    user_db = User()
    user = user_db.get_user(name)
    if password == user['password']:
        print 'before session'
        request.session['name'] = name
        roles = user['roles']
        print 'ok'
        return {'status': 'ok', 'roles': roles}
    else:
        return {'status':'nok'}

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

@view_config(renderer='templates/manage.pt')
def manage(request):
    name = request.session['name']
    return {'name':name}


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
    config.add_route('index', '')
    config.add_static_view(name='static', path='/Users/veronica/Documents/pyramid2/static')
    config.add_view(hello_world, route_name='hello')
    config.add_view(index, route_name='index', renderer='__main__:templates/index.pt')
    config.add_view(first, route_name='first', renderer='__main__:templates/first.pt')
    config.add_view(manage, route_name='manage', renderer='__main__:templates/manage.pt')
    config.add_view(login, route_name='login', renderer='json')
    config.add_view(logout, route_name='logout', renderer='json')
    config.add_view(get_all_users, route_name='get_all_users', renderer='string')
    config.add_view(get_all_permissions, route_name='get_all_permissions', renderer='string')
    config.add_view(operate_permission, route_name='operate_permission', renderer='string')
    config.add_view(get_all_roles, route_name='get_all_roles', renderer='string')
    config.add_view(operate_role, route_name='operate_role', renderer='string')
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
