import pytest
import inspect

from pathlib import Path
from .utils import *

admin = Path.cwd() / 'cms' / 'admin'

@pytest.mark.test_folder_structure_module1
def test_folder_structure_module1():
    assert Path.exists(admin) and Path.is_dir(admin), \
        'Have you created the `admin` blueprint folder?'

    module_file = admin / '__init__.py'
    assert Path.exists(module_file) and Path.is_file(module_file), \
        'Have you added the `__init__.py` file to the `admin` blueprint folder?'

@pytest.mark.test_models_file_module1
def test_models_file_module1():
    models_file = admin / 'models.py'
    assert Path.exists(models_file) and Path.is_file(models_file), \
        'Have you added the `models.py` file to the `admin` blueprint folder?'

@pytest.mark.test_move_models_module1
def test_move_models_module1():
    assert False, ''

@pytest.mark.test_import_models_module1
def test_import_models_module1():
    assert False, ''

@pytest.mark.test_create_blueprint_module1
def test_create_blueprint_module1():
    assert False, ''

@pytest.mark.test_move_routes_module1
def test_move_routes_module1():
    assert False, ''

@pytest.mark.test_register_blueprint_module1
def test_register_blueprint_module1():
    assert False, ''

@pytest.mark.test_template_folder_module1
def test_template_folder_module1():
    admin_templates = admin / 'templates'
    assert Path.exists(admin_templates) and Path.is_dir(admin_templates), \
        'Have you created a `templates` folder in the `admin` blueprint folder?'

    move = admin_templates / 'admin'
    assert Path.exists(move) and Path.is_dir(move), \
        'Have you move the `admin` folder from the root `templates` folder to the `admin` blueprint `templates` folder?'

    content =      move / 'content.html'
    content_form = move / 'content_form.html'
    layout =       move / 'layout.html'
    settings =     move / 'settings.html'
    users =        move / 'users.html'
    assert Path.exists(content) and Path.is_file(content)  \
        'Is the `content.html` template file in the `cms/admin/templates/admin` folder?'
    assert Path.exists(content_form) and Path.is_file(content_form) \
        'Is the `content_form.html` template file in the `cms/admin/templates/admin` folder?'
    assert Path.exists(layout) and Path.is_file(layout) \
        'Is the `layout.html` template file in the `cms/admin/templates/admin` folder?'
    assert Path.exists(settings) and Path.is_file(settings) \
        'Is the `settings.html` template file in the `cms/admin/templates/admin` folder?'
    assert Path.exists(users) and Path.is_file(users), \
        'Is the `users.html` template file in the `cms/admin/templates/admin` folder?'
