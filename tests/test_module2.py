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

    assert len(select_code(select_template_code[0], '<option', '</option>')) > 0, \
        'Have you added an `<option>` element inside the `for` loop?'

    links = template_functions('content_form', 'url_for')
    assert 'admin.content:type:type_name' in links, \
        'Do you have an `href` with a call to `url_for` pointing to `admin.content` passing in `type=type_name`?'
    assert False, ''

@pytest.mark.test_adjust_create_route_data_module2
def test_adjust_create_route_data_module2():
    assert False, ''

@pytest.mark.test_form_data_module2
def test_form_data_module2():
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
