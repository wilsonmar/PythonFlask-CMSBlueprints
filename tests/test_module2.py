import pytest
from pathlib import Path
from redbaron import RedBaron

from tests.utils import *

admin = Path.cwd() / 'cms' / 'admin'
admin_module = admin / '__init__.py'
admin_templates = admin / 'templates' / 'admin'
content_form = admin_templates / 'content_form.html'

admin_exists = Path.exists(admin) and Path.is_dir(admin)
admin_templates_exists = Path.exists(admin_templates) and Path.is_dir(admin_templates)
content_form_exists = Path.exists(content_form) and Path.is_file(content_form)
content_form_template = template_data('content_form')

with open(admin_module.resolve(), 'r') as admin_module_source_code:
    admin_module_code = RedBaron(admin_module_source_code.read())

def get_route(name):
    route = admin_module_code.find('def', name=name)
    assert route is not None, 'Have you moved the `{}` route to `admin/__init__.py`?'.format(name)
    return route

def get_methods_keyword(name):
    methods_keyword = get_route(name).find_all('call_argument', lambda node: str(node.target) == 'methods')
    assert methods_keyword is not None, 'Does the `{}` route have a keyword argument of `methods`?'.format(name)
    return methods_keyword

def get_request_method(name, parent=True):
    request_method = get_route(name).find('comparison', lambda node: \
        'request.method' in [str(node.first), str(node.second)])
    assert request_method is not None, 'Do you have an `if` statement that tests `request.method`?'
    return request_method.parent if parent else request_method

def get_form_data(name):
    variable = get_request_method('create').find_all('assign', lambda node: node.target.value == name)
    assert variable is not None, 'Do you have a variable named `' + name + '`?'
    right = variable.find('atomtrailers')
    assert right is not None, 'Are you setting the `' + name + '` variable correctly?'
    assert len(right) == 3 and \
        right[0].value == 'request' and \
        right[1].value == 'form' and \
        str(right[2]).replace("'", '"') == '["' + name + '"]', \
        'Are you setting the `' + name + '` varaible to request.form["' + name + '"]?'

@pytest.mark.test_add_from_controls_module2
def test_add_from_controls_module2():
    assert admin_exists and admin_templates_exists, \
        'Have you created a `templates` folder in the `admin` blueprint folder?'
    assert content_form_exists, \
        'Is the `content_form.html` file in the `admin/templates` folder?'
    title_el = content_form_template.select('input[name="title"][class="input"][type="text"]')
    assert len(title_el) == 1, 'Have you added an `<input>` with the correct attributes to the `title` control `<div>`?'
    slug_el = content_form_template.select('input[name="slug"][class="input"][type="text"]')
    assert len(slug_el) == 1, 'Have you added an `<input>` with the correct attributes to the `slug` control `<div>`?'
    body_el = content_form_template.select('textarea[name="body"][class="textarea"]')
    assert len(body_el) == 1, 'Have you added an `<textarea>` with the correct attributes to the `content` control `<div>`?'
    submit_el = content_form_template.select('input[type="submit"][value="Submit"]')
    assert len(submit_el) == 1, 'Have you added an `<input>` with the correct attributes to the first `is-grouped` control `<div>`?'
    cancel_el = content_form_template.select('a.button.is-text')
    assert len(cancel_el) == 1, 'Have you added an `<a>` with the correct attributes to the second `is-grouped` control `<div>`?'
    select_el = content_form_template.select('select[name="type_id"]')
    assert len(select_el) == 1, 'Have you added a `<select>` with the correct attributes to the `type` control `<div>`?'

    select_template_code = select_code('content_form', '<select', '</select>')
    assert len(select_template_code) > 0 and is_for(select_template_code[0]), 'Do you have a `for` loop in your `<select>` element?'
    assert select_template_code[0].target.name == 'type' and select_template_code[0].iter.name == 'types', \
        'Is the for loop cycling through `types`?'

    option_el = select_code(select_template_code[0], '<option', '</option>')
    assert len(option_el) > 0, 'Have you added an `<option>` element inside the `for` loop?'

    assert simplify(option_el[0]) == 'type.id', 'Is the `value` attribute set to `type.id`?'

    assert simplify(if_statements('content_form')) == 'type.name.eq.type_name.selected.None', \
        'Do you have an `if` statement in the `<option>` to test whether `type.name` is equal to `type_name`?'

    type_name = select_code(select_template_code[0], '>', '</option>')
    assert simplify(type_name[0]) == 'type.name', \
        'Are you adding `type.name` as the option name?'

    links = template_functions('content_form', 'url_for')
    assert 'admin.content:type:type_name' in links, \
        'Do you have an `href` with a call to `url_for` pointing to `admin.content` passing in `type=type_name`?'

@pytest.mark.test_adjust_create_route_data_module2
def test_adjust_create_route_data_module2():
    strings = list(get_methods_keyword('create').find_all('string').map(lambda node: node.value.replace("'", '"')))
    assert '"GET"' in strings and '"POST"' in strings, \
        'Have you added the `methods` keyword argument to the `create` route allowing `POST` and `GET`?'
    assert str(get_request_method('create', False)).find('POST'), 'Are you testing if the request method is `POST`?'
    title = get_request_method('create').find_all('assign', lambda node: node.target.value == 'title')
    assert title is not None, 'Do you have a variable named `title`?'
    right = title.find('atomtrailers')
    assert len(right) == 3 and \
        right[0].value == 'request' and \
        right[1].value == 'form' and \
        str(right[2]).replace("'", '"') == '["title"]', \
        'Are you setting the `title` varaible to request.form["title"]?'

@pytest.mark.test_form_data_module2
def test_form_data_module2():
    get_form_data('slug')
    get_form_data('type_id')
    get_form_data('body')

    error = get_request_method('create').find('assign', lambda node: node.target.value == 'error')
    assert error is not None, 'Do you have a variable named `error`?'
    assert error.value.to_python() is None, 'Are you setting the `error` variable correctly?'

@pytest.mark.test_validate_create_data_module2
def test_validate_create_data_module2():
    request_method_if  = get_request_method('create')
    title_error = request_method_if.find('unitary_operator', lambda node: node.target.value == 'title')
    assert title_error is not None and title_error.parent is not None and title_error.parent.type == 'if', \
        'Do you have an `if` statement that tests if `title` is `not` empty.'
    title_error_message = title_error.parent.find('assign', lambda node: node.target.value == 'error')
    assert title_error_message is not None and title_error_message.value.type == 'string', \
        'Are you setting the `error` variable to the appropriate `string` in the `if` statement.'

    type_error = request_method_if.find('unitary_operator', lambda node: node.target.value == 'type')
    assert type_error is not None and type_error.parent is not None and type_error.parent.type == 'elif', \
        'Do you have an `if` statement that tests if `type` is `not` empty.'
    type_error_message = type_error.parent.find('assign', lambda node: node.target.value == 'error')
    assert type_error_message is not None and type_error_message.value.type == 'string', \
        'Are you setting the `error` variable to the appropriate `string` in the `elif` statement.'

@pytest.mark.test_add_data_module2
def test_add_data_module2():
    request_method_if  = get_request_method('create')
    error_check = request_method_if.find('comparison', lambda node: \
        'error' in [str(node.first), str(node.second)])
    assert error_check is not None and error_check.parent.type == 'if' and \
        ((error_check.first.value == 'error' and error_check.second.value == 'None') or \
        (error_check.first.value == 'None' and error_check.second.value == 'error')) and \
        (error_check.value.first == '==' or error_check.value.first == 'is'), \
        'Do you have an if statment that is checking if `error` is `None`?'

    error_check_if = error_check.parent
    content = error_check_if.find('assign', lambda node: node.target.value == 'content')
    assert content is not None, 'Are you setting the `content` variable correctly?'
    content_instance = content.find('atomtrailers', lambda node: node.value[0].value == 'Content')
    assert content_instance is not None, 'Are you setting the `content` to an instance of `Content`?'
    content_args = list(content_instance.find_all('call_argument').map(lambda node: node.target.value + ':' + node.value.value))

    assert 'title:title' in content_args, \
        'Are you passing a `title` keyword argument set to `title` to the Content instance?'
    assert 'slug:slug' in content_args, \
        'Are you passing a `slug` keyword argument set to `slug` to the Content instance?'
    assert 'type_id:type_id' in content_args, \
        'Are you passing a `type_id` keyword argument set to `type_id` to the Content instance?'
    assert 'body:body' in content_args, \
        'Are you passing a `body` keyword argument set to `body` to the Content instance?'

    add_call = error_check_if.find('atomtrailers', lambda node: \
        node.value[0].value == 'db' and \
        node.value[1].value == 'session' and \
        node.value[2].value == 'add' and \
        node.value[3].type == 'call' and \
        node.value[3].value[0].value.value == 'content'
        )
    assert add_call is not None, 'Are you calling the `db.session.add()` function and passing in the correct argument?'

    commit_call = error_check_if.find('atomtrailers', lambda node: \
        node.value[0].value == 'db' and \
        node.value[1].value == 'session' and \
        node.value[2].value == 'commit' and \
        node.value[3].type == 'call'
        )
    assert commit_call is not None, 'Are you calling the `db.session.commit()` function?'

    return_redirect = error_check_if.find('return', lambda node: \
        node.value[0].value == 'redirect' and \
        node.value[1].type == 'call')
    assert return_redirect is not None, 'Are you returning a call to the `redirect()` function?'

    url_for_call = return_redirect.find_all('atomtrailers', lambda node: \
        node.value[0].value == 'url_for' and \
        node.value[1].type == 'call')
    assert url_for_call is not None, 'Are you passing a call to the `url_for()` function to the `redirect()` function?'

    url_for_args = list(url_for_call.find_all('call_argument').map(lambda node: str(node.target) + ':' + node.value.value))
    assert "None:'content'" in url_for_args, \
        "Are you passing the `'content'` to the `url_for()` function?"
    assert  'type:type' in url_for_args, \
        'Are you passing a `type` keyword argument set to `type` to the `url_for()` function?'

    assert request_method_if.find_all('atomtrailers', lambda node: \
        node.value[0].value == 'flash' and \
        node.value[1].type == 'call' and \
        node.value[1].value[0].value.value == 'error') is not None, \
        'Are you flashing an `error` at the end of the `request.method` `if`?'

@pytest.mark.test_add_edit_route_module2
def test_add_edit_route_module2():
    assert False, ''

@pytest.mark.test_populate_form_controls_module2
def test_populate_form_controls_module2():
    assert False, ''

@pytest.mark.test_edit_form_data_module2
def test_edit_form_data_module2():
    assert False, ''

@pytest.mark.test_validate_edit_data_module2
def test_validate_edit_data_module2():
    assert False, ''

@pytest.mark.test_update_data_module2
def test_update_data_module2():
    assert False, ''
