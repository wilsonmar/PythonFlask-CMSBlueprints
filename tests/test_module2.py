import pytest
import re
from pathlib import Path
from redbaron import RedBaron

from tests.utils import *

admin = Path.cwd() / 'cms' / 'admin'
admin_module = admin / '__init__.py'
admin_templates = admin / 'templates' / 'admin'
content_form = admin_templates / 'content_form.html'
content_path = admin_templates / 'content.html'

admin_exists = Path.exists(admin) and Path.is_dir(admin)
admin_module_exists = Path.exists(admin_module) and Path.is_file(admin_module)
admin_templates_exists = Path.exists(admin_templates) and Path.is_dir(admin_templates)
content_form_exists = Path.exists(content_form) and Path.is_file(content_form)
content_exists = Path.exists(content_path) and Path.is_file(content_path)
content_form_template = template_data('content_form')

def admin_module_code():
    with open(admin_module.resolve(), 'r') as admin_module_source_code:
        return RedBaron(admin_module_source_code.read())

def get_route(route):
    route_function = admin_module_code().find('def', name=route)
    route_function_exists = route_function is not None
    assert route_function_exists, \
        'Does the `{}` route function exist in `cms/admin/__init__.py`?'.format(route)
    return route_function

def get_methods_keyword(route):
    methods_keyword = get_route(route).find_all('call_argument', lambda node: \
        str(node.target) == 'methods')
    methods_keyword_exists = methods_keyword is not None
    assert methods_keyword_exists, \
        'Does the `{}` route have a keyword argument of `methods`?'.format(name)
    return methods_keyword

def get_request_method(route, parent=True):
    request_method = get_route(route).find('comparison', lambda node: \
        'request.method' in [str(node.first), str(node.second)])
    request_method_exists = request_method is not None
    assert request_method_exists, \
        'Do you have an `if` statement in the `{}` route that checks `request.method`?'.format(route)
    return request_method.parent if parent else request_method

def get_form_data(route, name):
    assignment = get_request_method(route).find('assign', lambda node: \
        str(node.target) == name)
    assignment_exists = assignment is not None
    assert assignment_exists, \
        'Do you have a variable named `{}`?'.format(name)

    right = assignment.find('atomtrailers', lambda node: \
        node.value[0].value == 'request' and \
        node.value[1].value == 'form' and \
        len(node.value) == 3 and \
        str(node.value[2]).replace("'", '"') == '["{}"]'.format(name.replace('content.', ''))) is not None
    assert right, \
        'Are you setting the `{}` varaible to request.form["{}"]?'.format(name.replace('content.', ''))

@pytest.mark.test_template_add_from_controls_module2
def test_template_add_from_controls_module2():
    assert admin_module_exists, \
        'Have you created the `cms/admin/__init__.py` file?'
    assert admin_exists and admin_templates_exists, \
        'Have you created a `templates` folder in the `admin` blueprint folder?'
    assert content_form_exists, \
        'Is the `content_form.html` file in the `admin/templates` folder?'

    title_exists = len(content_form_template.select('input[name="title"][class="input"][type="text"]')) == 1
    assert title_exists, \
        'Have you added an `<input>` with the correct attributes to the `title` control `<div>`?'

    slug_exists = len(content_form_template.select('input[name="slug"][class="input"][type="text"]')) == 1
    assert slug_exists, \
        'Have you added an `<input>` with the correct attributes to the `slug` control `<div>`?'

    body_exists = len(content_form_template.select('textarea[name="body"][class="textarea"]')) == 1
    assert body_exists, \
        'Have you added an `<textarea>` with the correct attributes to the `content` control `<div>`?'

@pytest.mark.test_template_type_dropdown_module2
def test_template_type_dropdown_module2():
    assert admin_module_exists, \
        'Have you created the `cms/admin/__init__.py` file?'
    assert admin_exists and admin_templates_exists, \
        'Have you created a `templates` folder in the `admin` blueprint folder?'
    assert content_form_exists, \
        'Is the `content_form.html` file in the `admin/templates` folder?'

    select_exists = len(content_form_template.select('select[name="type_id"]')) == 1
    assert select_exists, \
        'Have you added a `<select>` with the correct attributes to the `type` control `<div>`?'

    select_template_code = select_code('content_form', '<select', '</select>')
    for_loop = len(select_template_code) > 0 and is_for(select_template_code[0])
    assert for_loop, \
        'Do you have a `for` loop in your `<select>` element?'

    cycle_types = select_template_code[0].target.name == 'type' and select_template_code[0].iter.name == 'types'
    assert cycle_types, \
        'Is the for loop cycling through `types`?'

    option_el = select_code(select_template_code[0], '<option', '</option>')
    len_option = len(option_el) > 0
    assert len_option, \
        'Have you added an `<option>` element inside the `for` loop?'

    type_id = simplify(option_el[0]) == 'type.id'
    assert type_id, \
        'Is the `value` attribute set to `type.id`?'

    selected = simplify(if_statements('content_form')) == 'type.name.eq.type_name.selected.None'
    assert selected, \
        'Do you have an `if` statement in the `<option>` to test whether `type.name` is equal to `type_name`?'

    type_name_exists = simplify(select_code(select_template_code[0], '>', '</option>')[0]) == 'type.name'
    assert type_name_exists, \
        'Are you adding `type.name` as the option name?'

@pytest.mark.test_template_buttons_module2
def test_template_buttons_module2():
    assert admin_module_exists, \
        'Have you created the `cms/admin/__init__.py` file?'
    assert admin_exists and admin_templates_exists, \
        'Have you created a `templates` folder in the `admin` blueprint folder?'
    assert content_form_exists, \
        'Is the `content_form.html` file in the `admin/templates` folder?'

    submit_exists = len(content_form_template.select('input[type="submit"][value="Submit"].button.is-link')) == 1
    assert submit_exists, \
        'Have you added an `<input>` with the correct attributes to the first `is-grouped` control `<div>`?'

    cancel_el = content_form_template.select('a.button.is-text')
    cancel_exists = len(cancel_el) == 1
    assert cancel_exists, \
        'Have you added an `<a>` with the correct attributes to the second `is-grouped` control `<div>`?'

    a_contents = (cancel_el[0].contents[0]).lower() == 'cancel'
    assert a_contents, \
        'Does your cancel link contain the word `Cancel`?'

    links = 'admin.content:type:type_name' in template_functions('content_form', 'url_for')
    assert links, \
        'Do you have an `href` with a call to `url_for` pointing to `admin.content` passing in `type=type_name`?'

@pytest.mark.test_create_route_methods_module2
def test_create_route_methods_module2():
    assert admin_module_exists, \
        'Have you created the `cms/admin/__init__.py` file?'

    flask_import = admin_module_code().find('from_import', lambda node: node.value[0].value == 'flask')
    flask_import_exits = flask_import  is not None
    assert flask_import_exits, \
        'Do you have an import from `flask` statement?'
    from_flask_imports = list(flask_import.targets.find_all('name_as_name').map(lambda node: node.value ))
    request_import = 'request' in from_flask_imports
    assert request_import, \
        'Are you importing `request` from `flask` in `cms/admin/__init__.py`?'

    strings = list(get_methods_keyword('create').find_all('string').map(lambda node: node.value.replace("'", '"')))
    methods_exist = '"GET"' in strings and '"POST"' in strings
    assert methods_exist, \
        'Have you added the `methods` keyword argument to the `create` route allowing `POST` and `GET`?'
    post_check = str(get_request_method('create', False)).find('POST')
    assert post_check, 'Are you testing if the request method is `POST`?'
    get_form_data('create', 'title')

@pytest.mark.test_create_route_form_data_module2
def test_create_route_form_data_module2():
    assert admin_module_exists, \
        'Have you created the `cms/admin/__init__.py` file?'
    get_form_data('create', 'slug')
    get_form_data('create', 'type_id')
    get_form_data('create', 'body')

    error = get_request_method('create').find('assign', lambda node: \
        node.target.value == 'error')
    error_exists = error is not None
    assert error_exists, \
        'Do you have a variable named `error`?'
    error_none = error.value.to_python() is None
    assert error_none, \
        'Are you setting the `error` variable correctly?'

@pytest.mark.test_create_route_validate_data_module2
def test_create_route_validate_data_module2():
    assert admin_module_exists, \
        'Have you created the `cms/admin/__init__.py` file?'

    title_error = get_request_method('create').find('unitary_operator', lambda node: node.target.value == 'title')
    title_if_exists = title_error is not None and title_error.parent is not None and title_error.parent.type == 'if'
    assert title_if_exists, \
        'Do you have a nested `if` statement that tests if `title` is `not` empty.'
    title_error_message = title_error.parent.find('assign', lambda node: node.target.value == 'error')
    title_error_message_exists = title_error_message is not None and title_error_message.value.type == 'string'
    assert title_error_message_exists, \
        'Are you setting the `error` variable to the appropriate `string` in the `if` statement.'

    type_id_error = get_request_method('create').find('unitary_operator', lambda node: node.target.value == 'type_id')
    type_id_elif_exists = type_id_error is not None and type_id_error.parent is not None and type_id_error.parent.type == 'elif'
    assert type_id_elif_exists, \
        'Do you have a nested `if` statement that tests if `type` is `not` empty.'
    type_id_error_message = type_id_error.parent.find('assign', lambda node: node.target.value == 'error')
    type_id_error_message_exists = type_id_error_message is not None and type_id_error_message.value.type == 'string'
    assert type_id_error_message_exists, \
        'Are you setting the `error` variable to the appropriate `string` in the `elif` statement.'

@pytest.mark.test_create_route_insert_data_module2
def test_create_route_insert_data_module2():
    assert admin_module_exists, \
        'Have you created the `cms/admin/__init__.py` file?'
    error_check = get_request_method('create').find('comparison', lambda node: \
        'error' in [str(node.first), str(node.second)])
    error_check_exists = error_check is not None and error_check.parent.type == 'if' and \
        ((error_check.first.value == 'error' and error_check.second.value == 'None') or \
        (error_check.first.value == 'None' and error_check.second.value == 'error')) and \
        (error_check.value.first == '==' or error_check.value.first == 'is')
    assert error_check_exists, \
        'Do you have an `if` statment that is checking if `error` is `None`?'

    error_check_if = error_check.parent
    content = error_check_if.find('assign', lambda node: \
        node.target.value == 'content')
    content_exists = content is not None
    assert content_exists, \
        'Are you setting the `content` variable correctly?'
    content_instance = content.find('atomtrailers', lambda node: \
        node.value[0].value == 'Content')
    content_instance_exists = content_instance is not None
    assert content_instance_exists, \
        'Are you setting the `content` variable to an instance of `Content`?'
    content_args = list(content_instance.find_all('call_argument').map(lambda node: \
        node.target.value + ':' + node.value.value))

    title_exists = 'title:title' in content_args
    assert title_exists, \
        'Are you passing a `title` keyword argument set to `title` to the `Content` instance?'

    slug_exists = 'slug:slug' in content_args
    assert slug_exists, \
        'Are you passing a `slug` keyword argument set to `slug` to the `Content` instance?'

    type_id_exists = 'type_id:type_id' in content_args
    assert type_id_exists, \
        'Are you passing a `type_id` keyword argument set to `type_id` to the `Content` instance?'

    body_exists = 'body:body' in content_args
    assert body_exists, \
        'Are you passing a `body` keyword argument set to `body` to the `Content` instance?'

    content_count = len(content_args) == 4
    assert content_count, \
        'Are you passing the correct number of keyword arguments to the `Content` instance?'

    module_import = admin_module_code().find('from_import', lambda node: \
        node.find('name', value='models'))
    module_import_exists =  module_import is not None
    assert module_import_exists, \
        'Are you importing the correct methods and classes from `cms.admin.models`?'
    model_path = list(module_import.find_all('name').map(lambda node: node.value))
    import_path = module_import is not None and ':'.join(model_path) == 'cms:admin:models'
    assert import_path, \
        'Are you importing the correct methods and classes from `cms.admin.models` in `cms/__init__.py`?'

    name_as_name_db = module_import.find('name_as_name', value='db') is not None
    assert name_as_name_db, \
        'Are you importing the `db` SQLAlchemy instance from `cms.admin.models` in `admin/cms/__init__.py`?'


    add_call = error_check_if.find('atomtrailers', lambda node: \
        node.value[0].value == 'db' and \
        node.value[1].value == 'session' and \
        node.value[2].value == 'add' and \
        node.value[3].type == 'call' and \
        node.value[3].value[0].value.value == 'content'
        ) is not None
    assert add_call, \
        'Are you calling the `db.session.add()` function and passing in the correct argument?'

    commit_call = error_check_if.find('atomtrailers', lambda node: \
        node.value[0].value == 'db' and \
        node.value[1].value == 'session' and \
        node.value[2].value == 'commit' and \
        node.value[3].type == 'call'
        ) is not None
    assert commit_call, \
        'Are you calling the `db.session.commit()` function?'

@pytest.mark.test_create_route_redirect_module2
def test_create_route_redirect_module2():
    assert admin_module_exists, \
        'Have you created the `cms/admin/__init__.py` file?'

    flask_import = admin_module_code().find('from_import', lambda node: node.value[0].value == 'flask')
    flask_import_exits = flask_import  is not None
    assert flask_import_exits, \
        'Do you have an import from `flask` statement?'
    from_flask_imports = list(flask_import.targets.find_all('name_as_name').map(lambda node: node.value ))
    redirect_import = 'redirect' in from_flask_imports
    assert redirect_import, \
        'Are you importing `redirect` from `flask` in `cms/admin/__init__.py`?'
    url_for_import = 'url_for' in from_flask_imports
    assert url_for_import, \
        'Are you importing `url_for` from `flask` in `cms/admin/__init__.py`?'

    error_check = get_request_method('create').find('comparison', lambda node: \
        'error' in [str(node.first), str(node.second)])
    error_check_exists = error_check is not None and error_check.parent.type == 'if' and \
        ((error_check.first.value == 'error' and error_check.second.value == 'None') or \
        (error_check.first.value == 'None' and error_check.second.value == 'error')) and \
        (error_check.value.first == '==' or error_check.value.first == 'is')
    assert error_check_exists, \
        'Do you have an `if` statment that is checking if `error` is `None`?'
    error_check_if = error_check.parent

    return_redirect = error_check_if.find('return', lambda node: \
        node.value[0].value == 'redirect' and \
        node.value[1].type == 'call')
    return_redirect_exists = return_redirect is not None
    assert return_redirect_exists, \
        'Are you returning a call to the `redirect()` function?'

    url_for_call = return_redirect.find_all('atomtrailers', lambda node: \
        node.value[0].value == 'url_for' and \
        node.value[1].type == 'call')
    url_for_call_exists = url_for_call is not None
    assert url_for_call_exists, \
        'Are you passing a call to the `url_for()` function to the `redirect()` function?'

    url_for_args = list(url_for_call.find_all('call_argument').map(lambda node: str(node.target) + ':' + str(node.value.value).replace("'", '"')))
    url_content = 'None:"admin.content"' in url_for_args
    assert url_content, \
        "Are you passing the `'admin.content'` route to the `url_for()` function?"

    url_type = 'type:type' in url_for_args
    assert url_type, \
        'Are you passing a `type` keyword argument set to `type` to the `url_for()` function?'

    flash_exists = get_request_method('create').find('atomtrailers', lambda node: \
        node.value[0].value == 'flash' and \
        node.value[1].type == 'call' and \
        node.value[1].value[0].value.value == 'error') is not None
    assert flash_exists, \
        'Are you flashing an `error` at the end of the `request.method` `if`?'

@pytest.mark.test_edit_route_module2
def test_edit_route_module2():
    assert admin_module_exists, \
        'Have you created the `cms/admin/__init__.py` file?'
    accept_id = get_route('edit')\
        .find('def_argument', lambda node: node.target.value == 'id') is not None
    assert accept_id, \
        'Is the `edit` route function accepting an argument of `id`?'

    content = get_route('edit').find('assign', lambda node: node.target.value == 'content')
    content_exists = content is not None
    assert content_exists, \
        'Are you setting the `content` variable correctly?'
    query_call = content.find('atomtrailers', lambda node: \
        node.value[0].value == 'Content' and \
        node.value[1].value == 'query' and \
        node.value[2].value == 'get_or_404' and \
        node.value[3].type == 'call' and \
        node.value[3].value[0].value.value == 'id'
        ) is not None
    assert query_call, \
        'Are you calling the `Content.query.get_or_404()` function and are you passing in the correct argument?'

    edit_decorator = get_route('edit').find('dotted_name', lambda node: \
        node.value[0].value == 'admin_bp' and \
        node.value[1].type == 'dot' and \
        node.value[2].value == 'route' and \
        node.parent.call.type == 'call' and \
        bool(re.search('/admin/edit/<(int:)?id>', node.parent.call.value[0].value.value))
        ) is not None
    assert edit_decorator, \
        'Have you add a route decorator to the `edit` route function? Are you passing the correct route pattern?'

    strings = list(get_methods_keyword('edit').find_all('string').map(lambda node: node.value.replace("'", '"')))
    post_check = '"GET"' in strings and '"POST"' in strings
    assert post_check, \
        'Have you added the `methods` keyword argument to the `edit` route allowing `POST` and `GET`?'

@pytest.mark.test_edit_route_queries_module2
def test_edit_route_queries_module2():
    assert admin_module_exists, \
        'Have you created the `cms/admin/__init__.py` file?'

    type = get_route('edit').find('assign', lambda node: \
        node.target.value == 'type')
    type_exists = type is not None
    assert type_exists, \
        'Are you setting the `type` variable correctly?'
    get_call = type.find('atomtrailers', lambda node: \
        node.value[0].value == 'Type' and \
        node.value[1].value == 'query' and \
        node.value[2].value == 'get' and \
        node.value[3].type == 'call'
        )
    get_call_exists = get_call is not None
    assert get_call_exists, \
        'Are you calling the `Type.query.get()` function and assigning the result to `type`?'

    get_call_argument = get_call.find('call_argument', lambda node: \
        node.value[0].value == 'content' and \
        node.value[1].value == 'type_id') is not None
    assert get_call_argument, \
        'Are you passing the correct argument to the `Type.query.get()` function?'

    types = get_route('edit').find('assign', lambda node: \
        node.target.value == 'types')
    types_exists = types is not None
    assert types_exists, \
        'Are you setting the `types` variable correctly?'
    all_call = types.find('atomtrailers', lambda node: \
        node.value[0].value == 'Type' and \
        node.value[1].value == 'query' and \
        node.value[2].value == 'all' and \
        node.value[3].type == 'call'
        ) is not None
    assert all_call, \
        'Are you calling the `Type.query.all()` function and assigning the result to `types`?'

@pytest.mark.test_edit_route_render_template_module2
def test_edit_route_render_template_module2():
    assert admin_module_exists, \
        'Have you created the `cms/admin/__init__.py` file?'

    return_render = get_route('edit').find('return', lambda node: \
        node.value[0].value == 'render_template' and \
        node.value[1].type == 'call')
    return_render_exists = return_render is not None
    assert return_render_exists, \
        'Are you returning a call to the `render_template()` function?'

    return_render_args = list(return_render.find_all('call_argument').map(lambda node: str(node.target) + ':' + str(node.value).replace("'", '"')))
    template_exists = 'None:"admin/content_form.html"' in return_render_args
    assert template_exists, \
        'Are you passing the correct HTML template to the `render_template()` function?'

    types_exists = 'types:types' in return_render_args
    assert types_exists, \
        'Are you passing a `types` keyword argument set to `types` to the `render_template()` function?'

    title_exists = 'title:"Edit"' in return_render_args
    assert title_exists, \
        'Are you passing a `title` keyword argument set to `"Edit"` to the `render_template()` function?'

    item_title_exists = 'item_title:content.title' in return_render_args
    assert item_title_exists, \
        'Are you passing a `item_title` keyword argument set to `content.title` to the `render_template()` function?'

    slug_exists = 'slug:content.slug' in return_render_args
    assert slug_exists, \
        'Are you passing a `slug` keyword argument set to `content.slug` to the `render_template()` function?'

    type_name_exists = 'type_name:type.name' in return_render_args
    assert type_name_exists, \
        'Are you passing a `type_name` keyword argument set to `type.name` to the `render_template()` function?'

    type_id_exists = 'type_id:content.type_id' in return_render_args
    assert type_id_exists, \
        'Are you passing a `type_id` keyword argument set to `content.type_id` to the `render_template()` function?'

    body_exists = 'body:content.body' in return_render_args
    assert body_exists, \
        'Are you passing a `body` keyword argument set to `content.body` to the `render_template()` function?'

    argument_count = len(return_render_args) == 8
    assert argument_count, \
        'Are you passing the correct number of keyword arguments to the `render_template()` function?'

@pytest.mark.test_template_populate_form_controls_module2
def test_template_populate_form_controls_module2():
    assert admin_module_exists, \
        'Have you created the `cms/admin/__init__.py` file?'

    content_form_filters = filters('content_form')
    title_filter = 'item_title.default...None.None' in content_form_filters
    assert title_filter, \
        'Is _title_ `<input>` `value` attribute set to `item_title`? Have you added the `default(\'\')` filter?'

    slug_filter = 'slug.default...None.None' in content_form_filters
    assert slug_filter, \
        'Is _slug_ `<input>` `value` attribute set to `item_title`? Have you added the `default(\'\')` filter?'

    body_filter = 'body.default...None.None' in content_form_filters
    assert body_filter, \
        'Is _body_ `<textarea>` text content set to `body`? Have you added the `default(\'\')` filter?'

    assert content_exists, \
        'Is the `content.html` file in the `admin/templates` folder?'

    content_url_for = 'url_for.admin.edit.id.item.id.None.None' in get_calls('content')
    assert content_url_for, \
        'Do you have an `href` with a call to `url_for` pointing to `admin.edit` passing in `id=item.id`?'

@pytest.mark.test_edit_route_form_data_module2
def test_edit_route_form_data_module2():
    assert admin_module_exists, \
        'Have you created the `cms/admin/__init__.py` file?'

    post_check = str(get_request_method('edit', False)).find('POST')
    assert post_check, \
        'Are you testing if the request method is `POST`?'
    try:
        get_form_data('edit', 'content.title')
        get_form_data('edit', 'content.slug')
        get_form_data('edit', 'content.type_id')
        get_form_data('edit', 'content.body')
    except:
        assert False, 'Are you setting all proprties of the `content` object correctly?'

    content_updated_at = get_request_method('edit').find('assign', lambda node: \
        str(node.target) == 'content.updated_at')
    content_updated_at_exists = content_updated_at is not None
    assert content_updated_at_exists, \
        'Do you have a variable named `content_updated_at`?'
    right = content_updated_at.find('atomtrailers', lambda node: \
        node.value[0].value == 'datetime' and \
        node.value[1].value == 'utcnow' and \
        len(node.value) == 3 and \
        node.value[2].type == 'call') is not None
    assert right, \
        'Are you setting `content.updated_at` to the current date?'

    error = get_request_method('create').find('assign', lambda node: \
        node.target.value == 'error')
    error_exists = error is not None
    assert error_exists, \
        'Do you have a variable named `error`?'
    error_none = error.value.to_python() is None
    assert error_none, \
        'Are you setting the `error` variable correctly?'

@pytest.mark.test_edit_route_validate_data_module2
def test_edit_route_validate_data_module2():
    assert admin_module_exists, \
        'Have you created the `cms/admin/__init__.py` file?'
    title_error = get_request_method('edit').find('unitary_operator', lambda node: \
        node.target.value[0].value == 'request' and \
        node.target.value[1].value == 'form' and \
        len(node.target.value) == 3 and \
        str(node.target.value[2]).replace("'", '"') == '["{}"]'.format('title'))
    title_if_exists = title_error is not None and title_error.parent is not None and title_error.parent.type == 'if'
    assert title_if_exists, \
        'Do you have a nested `if` statement that tests if `title` is `not` empty.'

    title_error_message = title_error.parent.find('assign', lambda node: node.target.value == 'error')
    title_error_message_exists = title_error_message is not None and title_error_message.value.type == 'string'
    assert title_error_message_exists, \
        'Are you setting the `error` variable to the appropriate `string` in the `if` statement.'

@pytest.mark.test_edit_route_update_data_module2
def test_edit_route_update_data_module2():
    assert admin_module_exists, \
        'Have you created the `cms/admin/__init__.py` file?'
    error_check = get_request_method('edit').find('comparison', lambda node: \
        'error' in [str(node.first), str(node.second)])

    error_check_exists = error_check is not None and error_check.parent.type == 'if' and \
        ((error_check.first.value == 'error' and error_check.second.value == 'None') or \
        (error_check.first.value == 'None' and error_check.second.value == 'error')) and \
        (error_check.value.first == '==' or error_check.value.first == 'is')
    assert error_check_exists, \
        'Do you have an if statment that is checking if `error` is `None`?'

    error_check_if = error_check.parent
    commit_call = error_check_if.find('atomtrailers', lambda node: \
        node.value[0].value == 'db' and \
        node.value[1].value == 'session' and \
        node.value[2].value == 'commit' and \
        node.value[3].type == 'call'
        ) is not None
    assert commit_call, \
        'Are you calling the `db.session.commit()` function?'

    return_redirect = error_check_if.find('return', lambda node: \
        node.value[0].value == 'redirect' and \
        node.value[1].type == 'call')
    return_redirect_exists = return_redirect is not None
    assert return_redirect_exists, \
        'Are you returning a call to the `redirect()` function?'

    url_for_call = return_redirect.find_all('atomtrailers', lambda node: \
        node.value[0].value == 'url_for' and \
        node.value[1].type == 'call')
    url_for_call_exists = url_for_call is not None
    assert url_for_call_exists, \
        'Are you passing a call to the `url_for()` function to the `redirect()` function?'

    url_for_args = list(url_for_call.find_all('call_argument').map(lambda node: \
        str(node.target) + ':' + str(node.value).replace("'", '"')))
    url_content = 'None:"content"' in url_for_args
    assert url_content, \
        "Are you passing the `'content'` to the `url_for()` function?"

    url_type = 'type:type.name' in url_for_args
    assert url_type, \
        'Are you passing a `type` keyword argument set to `type.name` to the `url_for()` function?'

    flash_exists = get_request_method('create').find('atomtrailers', lambda node: \
        node.value[0].value == 'flash' and \
        node.value[1].type == 'call' and \
        node.value[1].value[0].value.value == 'error') is not None
    assert flash_exists, \
        'Are you flashing an `error` at the end of the `request.method` `if`?'
