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

def get_create_route():
    create_route = admin_module_code.find('def', name='create')
    assert create_route is not None, 'Have you moved the `create` route to `admin/__init__.py`?'
    return create_route

def get_create_method():
    create_method = get_create_route().find_all('call_argument', lambda node: str(node.target) == 'methods')
    assert create_method is not None, 'Does the `create` route have a keyword argument of `methods`?'
    return create_method

def get_request_method():
    request_method = get_create_route().find('comparison', lambda node: \
        'request.method' in [str(node.first), str(node.second)])
    assert request_method is not None, 'Do you have an `if` statement that tests `request.method`?'
    return request_method

def get_form_data(name):
    variable = get_request_method().parent.find_all('assign', lambda node: node.target.value == name)
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
    strings = list(get_create_method().find_all('string').map(lambda node: node.value.replace("'", '"')))
    assert '"GET"' in strings and '"POST"' in strings, \
        'Have you added the `methods` keyword argument to the `create` route allowing `POST` and `GET`?'
    assert str(get_request_method()).find('POST'), 'Are you testing if the request method is `POST`?'
    title = get_request_method().parent.find_all('assign', lambda node: node.target.value == 'title')
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

    error = get_request_method().parent.find_all('assign', lambda node: node.target.value == 'error')
    assert error is not None, 'Do you have a variable named `error`?'
    # right = error.find('name')
    # assert right is not None, 'Are you setting the `error` variable correctly?'
    # print(right)
    assert False, ''
    

@pytest.mark.test_validate_create_data_module2
def test_validate_create_data_module2():
    assert False, ''

@pytest.mark.test_add_data_module2
def test_add_data_module2():
    assert False, ''

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
