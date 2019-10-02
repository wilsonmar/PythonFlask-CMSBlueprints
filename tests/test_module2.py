import pytest
import re
from pathlib import Path
from redbaron import RedBaron

from tests.utils import *

admin = Path.cwd() / 'cms' / 'admin'
admin_module = admin / '__init__.py'
admin_templates = admin / 'templates' / 'admin'
content_form = admin_templates / 'content_form.html'

admin_exists = Path.exists(admin) and Path.is_dir(admin)
admin_module_exists = Path.exists(admin_module) and Path.is_file(admin_module)
admin_templates_exists = Path.exists(admin_templates) and Path.is_dir(admin_templates)
content_form_exists = Path.exists(content_form) and Path.is_file(content_form)
content_form_template = template_data('content_form')

def admin_module_code():
    with open(admin_module.resolve(), 'r') as admin_module_source_code:
        return RedBaron(admin_module_source_code.read())

def get_route(route):
    assert admin_exists, 'Have you created the `admin` blueprint folder?'
    assert admin_module_exists, 'Have you added the `__init__.py` file to the `admin` blueprint folder?'
    route_function = admin_module_code().find('def', name=route)
    assert route_function is not None, 'Does the `{}` route function exist in `admin/__init__.py`?'.format(route)
    return route_function

def get_methods_keyword(route):
    assert admin_exists, 'Have you created the `admin` blueprint folder?'
    assert admin_module_exists, 'Have you added the `__init__.py` file to the `admin` blueprint folder?'
    methods_keyword = get_route(route).find_all('call_argument', lambda node: str(node.target) == 'methods')
    assert methods_keyword is not None, 'Does the `{}` route have a keyword argument of `methods`?'.format(name)
    return methods_keyword

def get_request_method(route, parent=True):
    assert admin_exists, 'Have you created the `admin` blueprint folder?'
    assert admin_module_exists, 'Have you added the `__init__.py` file to the `admin` blueprint folder?'
    request_method = get_route(route).find('comparison', lambda node: \
        'request.method' in [str(node.first), str(node.second)])
    assert request_method is not None, 'Do you have an `if` statement that tests `request.method`?'
    return request_method.parent if parent else request_method

def get_form_data(route, name):
    variable = get_request_method(route).find('assign', lambda node: str(node.target) == name)
    assert variable is not None, 'Do you have a variable named `{}`?'.format(name)
    assert variable.find('atomtrailers', lambda node: \
        node.value[0].value == 'request' and \
        node.value[1].value == 'form' and \
        len(node.value) == 3 and \
        str(node.value[2]).replace("'", '"') == '["{}"]'.format(name.replace('content.', ''))) is not None, \
        'Are you setting the `{}` varaible to request.form["{}"]?'.format(name.replace('content.', ''))

create_request_method  = get_request_method('create')

edit_route = get_route('edit')
edit_request_method  = get_request_method('edit')

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
    assert admin_module_exists, 'Have you created the `admin/__init__.py` file?'
    strings = list(get_methods_keyword('create').find_all('string').map(lambda node: node.value.replace("'", '"')))
    assert '"GET"' in strings and '"POST"' in strings, \
        'Have you added the `methods` keyword argument to the `create` route allowing `POST` and `GET`?'
    assert str(get_request_method('create', False)).find('POST'), 'Are you testing if the request method is `POST`?'
    get_form_data('create', 'title')

@pytest.mark.test_form_data_module2
def test_form_data_module2():
    assert admin_module_exists, 'Have you created the `admin/__init__.py` file?'
    get_form_data('create', 'slug')
    get_form_data('create', 'type_id')
    get_form_data('create', 'body')

    error = create_request_method.find('assign', lambda node: node.target.value == 'error')
    assert error is not None, 'Do you have a variable named `error`?'
    assert error.value.to_python() is None, 'Are you setting the `error` variable correctly?'

@pytest.mark.test_validate_create_data_module2
def test_validate_create_data_module2():
    assert admin_module_exists, 'Have you created the `admin/__init__.py` file?'

    title_error = create_request_method.find('unitary_operator', lambda node: node.target.value == 'title')
    assert title_error is not None and title_error.parent is not None and title_error.parent.type == 'if', \
        'Do you have an `if` statement that tests if `title` is `not` empty.'
    title_error_message = title_error.parent.find('assign', lambda node: node.target.value == 'error')
    assert title_error_message is not None and title_error_message.value.type == 'string', \
        'Are you setting the `error` variable to the appropriate `string` in the `if` statement.'

    type_error = create_request_method.find('unitary_operator', lambda node: node.target.value == 'type')
    assert type_error is not None and type_error.parent is not None and type_error.parent.type == 'elif', \
        'Do you have an `if` statement that tests if `type` is `not` empty.'
    type_error_message = type_error.parent.find('assign', lambda node: node.target.value == 'error')
    assert type_error_message is not None and type_error_message.value.type == 'string', \
        'Are you setting the `error` variable to the appropriate `string` in the `elif` statement.'

@pytest.mark.test_add_data_module2
def test_add_data_module2():
    assert admin_module_exists, 'Have you created the `admin/__init__.py` file?'
    error_check = create_request_method.find('comparison', lambda node: \
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
        'Are you passing a `title` keyword argument set to `title` to the `Content` instance?'
    assert 'slug:slug' in content_args, \
        'Are you passing a `slug` keyword argument set to `slug` to the `Content` instance?'
    assert 'type_id:type_id' in content_args, \
        'Are you passing a `type_id` keyword argument set to `type_id` to the `Content` instance?'
    assert 'body:body' in content_args, \
        'Are you passing a `body` keyword argument set to `body` to the `Content` instance?'
    assert len(content_args) == 4, \
        'Are you passing the correct number of keyword arguments to the `Content` instance?'

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

    url_for_args = list(url_for_call.find_all('call_argument').map(lambda node: str(node.target) + ':' + str(node.value.value).replace("'", '"')))
    assert 'None:"content"' in url_for_args, \
        "Are you passing the `'content'` to the `url_for()` function?"
    assert  'type:type' in url_for_args, \
        'Are you passing a `type` keyword argument set to `type` to the `url_for()` function?'

    assert create_request_method.find_all('atomtrailers', lambda node: \
        node.value[0].value == 'flash' and \
        node.value[1].type == 'call' and \
        node.value[1].value[0].value.value == 'error') is not None, \
        'Are you flashing an `error` at the end of the `request.method` `if`?'

@pytest.mark.test_add_edit_route_module2
def test_add_edit_route_module2():
    assert admin_module_exists, 'Have you created the `admin/__init__.py` file?'
    assert edit_route.find('def_argument', lambda node: node.target.value == 'id') is not None, \
        'Is the `edit` route function accepting an argument of `id`?'

    content = edit_route.find('assign', lambda node: node.target.value == 'content')
    assert content is not None, 'Are you setting the `content` variable correctly?'
    query_call = content.find('atomtrailers', lambda node: \
        node.value[0].value == 'Content' and \
        node.value[1].value == 'query' and \
        node.value[2].value == 'get_or_404' and \
        node.value[3].type == 'call' and \
        node.value[3].value[0].value.value == 'id'
        )
    assert query_call is not None, 'Are you calling the `Content.query.get_or_404()` function and are you passing in the correct argument?'

    edit_decorator = edit_route.find('dotted_name', lambda node: \
        node.value[0].value == 'admin_bp' and \
        node.value[1].type == 'dot' and \
        node.value[2].value == 'route' and \
        node.parent.call.type == 'call' and \
        bool(re.search('/admin/edit/<(int:)?id>', node.parent.call.value[0].value.value))
        )
    assert edit_decorator is not None, 'Have you add a route decorator to the `edit` route function? Are you passing the correct route pattern?'

    strings = list(get_methods_keyword('edit').find_all('string').map(lambda node: node.value.replace("'", '"')))
    assert '"GET"' in strings and '"POST"' in strings, \
        'Have you added the `methods` keyword argument to the `edit` route allowing `POST` and `GET`?'

@pytest.mark.test_edit_route_render_template_module2
def test_edit_route_render_template_module2():
    assert admin_module_exists, 'Have you created the `admin/__init__.py` file?'
    type = edit_route.find('assign', lambda node: node.target.value == 'type')
    assert type is not None, 'Are you setting the `type` variable correctly?'
    get_call = type.find('atomtrailers', lambda node: \
        node.value[0].value == 'Type' and \
        node.value[1].value == 'query' and \
        node.value[2].value == 'get' and \
        node.value[3].type == 'call'
        )
    assert get_call is not None, 'Are you calling the `Type.query.get()` function and assigning the result to `type`?'
    assert get_call.find('call_argument', lambda node: \
        node.value[0].value == 'request' and \
        node.value[1].value == 'form' and \
        node.value[2].value.value.replace("'", '"') == '"type_id"') is not None, \
        'Are you passing the correct argument to the `Type.query.get()` function?'
    types = edit_route.find('assign', lambda node: node.target.value == 'types')
    assert types is not None, 'Are you setting the `types` variable correctly?'
    all_call = types.find('atomtrailers', lambda node: \
        node.value[0].value == 'Type' and \
        node.value[1].value == 'query' and \
        node.value[2].value == 'all' and \
        node.value[3].type == 'call'
        )
    assert all_call is not None, 'Are you calling the `Type.query.all()` function and assigning the result to `types`?'

    return_render = edit_route.find('return', lambda node: \
        node.value[0].value == 'render_template' and \
        node.value[1].type == 'call')
    assert return_render is not None, 'Are you returning a call to the `render_template()` function?'

    return_render_args = list(return_render.find_all('call_argument').map(lambda node: str(node.target) + ':' + str(node.value).replace("'", '"')))

    assert 'None:"admin/content_form.html"' in return_render_args, \
        'Are you passing the correct HTML template to the `render_template()` function?'
    assert 'types:types' in return_render_args, \
        'Are you passing a `types` keyword argument set to `types` to the `render_template()` function?'
    assert 'title:"Edit"' in return_render_args, \
        'Are you passing a `title` keyword argument set to `"Edit"` to the `render_template()` function?'
    assert 'item_title:content.title' in return_render_args, \
        'Are you passing a `item_title` keyword argument set to `content.title` to the `render_template()` function?'
    assert 'slug:content.slug' in return_render_args, \
        'Are you passing a `slug` keyword argument set to `content.slug` to the `render_template()` function?'
    assert 'type_name:type.name' in return_render_args, \
        'Are you passing a `type_name` keyword argument set to `type.name` to the `render_template()` function?'
    assert 'type_id:content.type_id' in return_render_args, \
        'Are you passing a `type_id` keyword argument set to `content.type_id` to the `render_template()` function?'
    assert 'body:content.body' in return_render_args, \
        'Are you passing a `body` keyword argument set to `content.body` to the `render_template()` function?'
    assert len(return_render_args) == 8, \
        'Are you passing the correct number of keyword arguments to the `render_template()` function?'

@pytest.mark.test_populate_form_controls_module2
def test_populate_form_controls_module2():
    assert admin_module_exists, 'Have you created the `admin/__init__.py` file?'
    content_form_filters = filters('content_form')
    assert 'item_title.default...None.None' in content_form_filters, \
        'Have you given the `title` `<input>` a `value` attribute and set it to the `item_title` template variable? Make sure you have added the `default(\'\')` filter.'
    assert 'slug.default...None.None' in content_form_filters, \
        'Have you given the `slug` `<input>` a `value` attribute and set it to the `slug` template variable? Make sure you have added the `default(\'\')` filter.'
    assert 'body.default...None.None' in content_form_filters, \
        'Have you given the `body` `<textarea>` a `value` attribute and set it to the `body` template variable? Make sure you have added the `default(\'\')` filter.'

@pytest.mark.test_edit_form_data_module2
def test_edit_form_data_module2():
    assert admin_module_exists, 'Have you created the `admin/__init__.py` file?'
    assert str(get_request_method('edit', False)).find('POST'), 'Are you testing if the request method is `POST`?'
    get_form_data('edit', 'content.title')
    get_form_data('edit', 'content.slug')
    get_form_data('edit', 'content.type_id')
    get_form_data('edit', 'content.body')

    error = create_request_method.find('assign', lambda node: node.target.value == 'error')
    assert error is not None, 'Do you have a variable named `error`?'
    assert error.value.to_python() is None, 'Are you setting the `error` variable correctly?'

@pytest.mark.test_validate_edit_data_module2
def test_validate_edit_data_module2():
    assert admin_module_exists, 'Have you created the `admin/__init__.py` file?'
    title_error = edit_request_method.find('unitary_operator', lambda node: \
        node.target.value[0].value == 'request' and \
        node.target.value[1].value == 'form' and \
        len(node.target.value) == 3 and \
        str(node.target.value[2]).replace("'", '"') == '["{}"]'.format('title'))
    assert title_error is not None and title_error.parent is not None and title_error.parent.type == 'if', \
        'Do you have an `if` statement that tests if `title` is `not` empty.'

    title_error_message = title_error.parent.find('assign', lambda node: node.target.value == 'error')
    assert title_error_message is not None and title_error_message.value.type == 'string', \
        'Are you setting the `error` variable to the appropriate `string` in the `if` statement.'

@pytest.mark.test_update_data_module2
def test_update_data_module2():
    assert admin_module_exists, 'Have you created the `admin/__init__.py` file?'
    error_check = edit_request_method.find('comparison', lambda node: \
        'error' in [str(node.first), str(node.second)])
    assert error_check is not None and error_check.parent.type == 'if' and \
        ((error_check.first.value == 'error' and error_check.second.value == 'None') or \
        (error_check.first.value == 'None' and error_check.second.value == 'error')) and \
        (error_check.value.first == '==' or error_check.value.first == 'is'), \
        'Do you have an if statment that is checking if `error` is `None`?'

    error_check_if = error_check.parent
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

    url_for_args = list(url_for_call.find_all('call_argument').map(lambda node: str(node.target) + ':' + str(node.value).replace("'", '"')))
    assert 'None:"content"' in url_for_args, \
        "Are you passing the `'content'` to the `url_for()` function?"
    assert  'type:type.name' in url_for_args, \
        'Are you passing a `type` keyword argument set to `type` to the `url_for()` function?'

    assert create_request_method.find_all('atomtrailers', lambda node: \
        node.value[0].value == 'flash' and \
        node.value[1].type == 'call' and \
        node.value[1].value[0].value.value == 'error') is not None, \
        'Are you flashing an `error` at the end of the `request.method` `if`?'