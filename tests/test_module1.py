import pytest

from pathlib import Path

from redbaron import RedBaron

main_module = Path.cwd() / 'cms' / '__init__.py'
admin = Path.cwd() / 'cms' / 'admin'
admin_exists = Path.exists(admin) and Path.is_dir(admin)
module = admin / '__init__.py'
module_exists = Path.exists(module) and Path.is_file(module)
models = admin / 'models.py'
models_exists = Path.exists(models) and Path.is_file(models)

@pytest.mark.test_folder_structure_module1
def test_folder_structure_module1():
    query = Query(models.resolve())
    print(query.select('classdef').dump())
    assert False, ''

with open(models.resolve(), 'r') as models_source_code:
    models_code = RedBaron(models_source_code.read())

with open(module.resolve(), 'r') as module_source_code:
    module_code = RedBaron(module_source_code.read())

with open(main_module.resolve(), 'r') as main_module_source_code:
    main_module_code = RedBaron(main_module_source_code.read())

@pytest.mark.test_folder_structure_module1
def test_folder_structure_module1():
    assert admin_exists, 'Have you created the `admin` blueprint folder?'
    assert module_exists, 'Have you added the `__init__.py` file to the `admin` blueprint folder?'

@pytest.mark.test_models_file_module1
def test_models_file_module1():
    assert models_exists, 'Have you added the `models.py` file to the `admin` blueprint folder?'

@pytest.mark.test_model_file_imports_module1
def test_model_file_imports_module1():
    assert models_exists, 'Have you added the `models.py` file to the `admin` blueprint folder?'

    import_sql = models_code.find('name', lambda node: \
        node.value == 'flask_sqlalchemy' and \
        node.parent.type == 'from_import' and \
        node.parent.targets[0].value == 'SQLAlchemy')
    assert import_sql is not None, 'Are you importing `SQLAlchemy` from `flask_sqlalchemy` at the top of `models.py`?'

    import_datetime = models_code.find('name', lambda node: \
        node.value == 'datetime' and \
        node.parent.type == 'from_import' and \
        node.parent.targets[0].value == 'datetime')
    assert import_datetime is not None, 'Are you importing `datetime` from `datetime`?'

    db_assignment = models_code.find('atomtrailers', lambda node: \
        node.value[0].value == 'SQLAlchemy' and \
        node.value[1].type == 'call' and \
        node.parent.type == 'assignment' and \
        node.parent.target.value == 'db')
    assert db_assignment is not None, 'Are you creating an new `SQLAlchemy` instance named `db`?'
    assert len(db_assignment.find_all('call_argument')) == 0, \
        'Are you passing arguments to the `SQLAlchemy` constructor? If so you can remove them.'

@pytest.mark.test_move_models_module1
def test_move_models_module1():
    assert models_exists, 'Have you added the `models.py` file to the `admin` blueprint folder?'

    model_classes = list(models_code.find_all('class').map(lambda node: node.name))
    assert len(model_classes) == 4, \
        'Have you moved the four models from `__init__.py` to `cms/admin/models.py`'
    assert 'Type' in model_classes, \
        'Have you moved the `Type` model from `__init__.py` to `cms/admin/models.py`'
    assert 'Content' in model_classes, \
        'Have you moved the `Content` model from `__init__.py` to `cms/admin/models.py`'
    assert 'Setting' in model_classes, \
        'Have you moved the `Setting` model from `__init__.py` to `cms/admin/models.py`'
    assert 'Type' in model_classes, \
        'Have you moved the `Type` model from `__init__.py` to `cms/admin/models.py`'

    main_module_classes = list(main_module_code.find_all('class').map(lambda node: node.name))
    assert len(main_module_classes) == 0, \
        'Have you moved the four models from `__init__.py` to `cms/admin/models.py`'

@pytest.mark.test_remove_models_module1
def test_remove_models_module1():
    db_assignment = main_module_code.find('atomtrailers', lambda node: \
        node.value[0].value == 'SQLAlchemy' and \
        node.value[1].type == 'call' and \
        node.parent.type == 'assignment' and \
        node.parent.target.value == 'db')
    assert db_assignment is None, 'Have you removed the `SQLAlchemy` instance named `db` from `__init__.py`?'

    main_import_sql = main_module_code.find('name', lambda node: \
        node.value == 'flask_sqlalchemy' and \
        node.parent.type == 'from_import' and \
        node.parent.targets.first.value == 'SQLAlchemy')
    assert main_import_sql is None, 'Have you removed the import for `flask_sqlalchemy` from `__init__.py`?'

    main_import_datetime = main_module_code.find('name', lambda node: \
        node.value == 'datetime' and \
        node.parent.type == 'from_import' and \
        node.parent.targets.first.value == 'datetime')
    assert main_import_datetime is None, 'Have you removed the import for `datetime` from `__init__.py`?'

@pytest.mark.test_import_models_module1
def test_import_models_module1():
    main_module_import = main_module_code.find('from_import', lambda node: node.find('name', value='models'))
    assert main_module_import is not None, 'Are you importing the correct methods and classes from `cms.admin.models`?'
    model_path = list(main_module_import.find_all('name').map(lambda node: node.value))
    assert main_module_import is not None and \
        ':'.join(model_path) == 'cms:admin:models', \
        'Are you importing the correct methods and classes from `cms.admin.models`?'

    assert main_module_import.find('name_as_name', value='db') is not None, \
        'Are you importing the `db` SQLAlchemy instance from `cms.admin.models`?'
    assert main_module_import.find('name_as_name', value='Content') is not None, \
        'Are you importing the `Content` model class from `cms.admin.models`?'
    assert main_module_import.find('name_as_name', value='Type') is not None, \
        'Are you importing the `Type` model class from `cms.admin.models`?'
    assert main_module_import.find('name_as_name', value='Setting') is not None, \
        'Are you importing the `Setting` model class from `cms.admin.models`?'
    assert main_module_import.find('name_as_name', value='User') is not None, \
        'Are you importing the `User` model class from `cms.admin.models`?'

    init_app_call = main_module_code.find('name', lambda node: \
        node.value == 'init_app' and \
        node.parent.value[0].value == 'db' and \
        node.parent.value[2].type == 'call')
    assert init_app_call is not None, 'Are you calling the `init_app` method on `db`?'
    init_app_arg = init_app_call.parent.find('call_argument').value.value
    assert init_app_arg == 'app', 'Are you passing `app` to the `init_app` method?'

@pytest.mark.test_create_blueprint_module1
def test_create_blueprint_module1():
    flask_import = module_code.find('from_import', lambda node: node.value[0].value == 'flask')
    assert flask_import is not None, 'Are you importing the correct methods and classes from `flask`?'
    from_flask_imports = list(flask_import.targets.find_all('name_as_name').map(lambda node: node.value ))
    assert 'Blueprint' in from_flask_imports, 'Are you importing `Blueprint` from `flask`?'

    blueprint_call = module_code.find('name', lambda node: \
        node.value == 'Blueprint' and \
        node.parent.value[1].type == 'call').parent
    blueprint_instance = blueprint_call.parent

    blueprint_args = list(blueprint_call.find_all('call_argument').map(lambda node: str(node.target) + ':' + str(node.value)))
    assert "None:'admin'" in blueprint_args, \
        "Are you passing the Blueprint instance the correct arguments? The first argument should be: `'admin'`."
    assert "None:__name__" in blueprint_args, \
        'Are you passing the Blueprint instance the correct arguments? The second argument should be: `__name__`.'
    assert "url_prefix:'/admin'" in blueprint_args, \
        "Are you passing the Blueprint instance the correct arguments? There should be a url_prefix keyword argument set to `'/admin'`."

@pytest.mark.test_admin_module_imports_module1
def test_admin_module_imports_module1():
    flask_import = module_code.find('from_import', lambda node: node.value[0].value == 'flask')
    assert flask_import is not None, 'Are you importing the correct methods and classes from `flask`?'
    from_flask_imports = list(flask_import.targets.find_all('name_as_name').map(lambda node: node.value ))
    assert 'render_template' in from_flask_imports, 'Are you importing `render_template` from `flask`?'
    assert 'abort' in from_flask_imports, 'Are you importing `abort` from `flask`?'

    module_import = module_code.find('from_import', lambda node: node.find('name', value='models'))
    assert module_import is not None, 'Are you importing the correct methods and classes from `cms.admin.models`?'
    model_path = list(module_import.find_all('name').map(lambda node: node.value))
    assert module_import is not None and \
        ':'.join(model_path) == 'cms:admin:models', \
        'Are you importing the correct methods and classes from `cms.admin.models`?'

    assert module_import.find('name_as_name', value='Content') is not None, \
        'Are you importing the `Content` model class from `cms.admin.models`?'
    assert module_import.find('name_as_name', value='Type') is not None, \
        'Are you importing the `Type` model class from `cms.admin.models`?'
    assert module_import.find('name_as_name', value='Setting') is not None, \
        'Are you importing the `Setting` model class from `cms.admin.models`?'
    assert module_import.find('name_as_name', value='User') is not None, \
        'Are you importing the `User` model class from `cms.admin.models`?'

@pytest.mark.test_move_routes_module1
def test_move_routes_module1():
    assert module_code.find('def', name='requested_type') is not None, \
        'Did you move the `requested_type` function from `__init__.py` to `admin/__init__.py`?'

    content_route = module_code.find('def', name='content')
    assert content_route is not None, \
        'Did you move the `content` function from `__init__.py` to `admin/__init__.py`?'
    content_decorators = content_route.find_all('dotted_name')
    assert len(content_decorators) == 2, 'Did you move both `content` route decorators to `admin/__init__.py`?'
    assert str(content_decorators[0]) == 'admin_bp.route', 'Have you changed the `@app` decorator to `@admin_ap` on the `create` function?'
    assert str(content_decorators[1]) == 'admin_bp.route', 'Have you changed the `@app` decorator to `@admin_ap` on the `create` function?'

    create_route = module_code.find('def', name='create')
    assert create_route is not None, \
        'Did you move the `create` function from `__init__.py` to `admin/__init__.py`?'
    create_decorators = create_route.find_all('dotted_name')
    assert len(create_decorators) == 1, 'Did you move the `create` route decorators to `admin/__init__.py`?'
    assert str(create_decorators[0]) == 'admin_bp.route', 'Have you changed the `@app` decorator to `@admin_ap` on the `create` function?'

    users_route = module_code.find('def', name='users')
    assert users_route is not None, \
        'Did you move the `users` function from `__init__.py` to `admin/__init__.py`?'
    users_decorators = users_route.find_all('dotted_name')
    assert len(users_decorators) == 1, 'Did you move the `users` route decorators to `admin/__init__.py`?'
    assert str(users_decorators[0]) == 'admin_bp.route', 'Have you changed the `@app` decorator to `@admin_ap` on the `users` function?'

    settings_route = module_code.find('def', name='settings')
    assert settings_route is not None, \
        'Did you move the `settings` function from `__init__.py` to `admin/__init__.py`?'
    settings_decorators = settings_route.find_all('dotted_name')
    assert len(settings_decorators) == 1, 'Did you move the `settings` route decorators to `admin/__init__.py`?'
    assert str(settings_decorators[0]) == 'admin_bp.route', 'Have you changed the `@app` decorator to `@admin_ap` on the `settings` function?'

    assert main_module_code.find('def', name='content') is None, \
        'Did you remove the `content` function from `__init__.py`?'

    assert main_module_code.find('def', name='create') is None, \
        'Did you remove the `create` function from `__init__.py`?'

    assert main_module_code.find('def', name='users') is None, \
        'Did you remove the `users` function from `__init__.py`?'

    assert main_module_code.find('def', name='settings') is  None, \
        'Did you remove the `settings` function from `__init__.py`?'

@pytest.mark.test_register_blueprint_module1
def test_register_blueprint_module1():
    bp_import = main_module_code.find('from_import', lambda node: node.find('name_as_name', value='admin_bp'))
    assert bp_import is not None, 'Are you importing `admin_bp` from `cms.admin`?'
    model_path = list(bp_import.find_all('name').map(lambda node: node.value))
    assert bp_import is not None and \
        ':'.join(model_path) == 'cms:admin', \
        'Are you importing the `admin_bp` Blueprint from `cms.admin`?'

    register_bp_call = main_module_code.find('atomtrailers', lambda node: \
        node.value[0].value == 'app' and \
        node.value[1].value == 'register_blueprint' and \
        node.value[2].type == 'call')
    assert register_bp_call is not None, 'Are you calling `register_blueprint` on `app`?'

    register_blueprint_args = list(register_bp_call.find_all('call_argument').map(lambda node: str(node.target) + ':' + str(node.value)))
    assert len(register_blueprint_args) == 1, \
        'Are you only passing one argument to `register_blueprint`?'
    assert "None:admin_bp" in register_blueprint_args, \
        'Are you passing the Blueprint instance to should be `register_blueprint`?'

@pytest.mark.test_template_folder_module1
def test_template_folder_module1():
    blueprint_call = module_code.find('name', lambda node: \
        node.value == 'Blueprint' and \
        node.parent.value[1].type == 'call').parent
    blueprint_instance = blueprint_call.parent

    blueprint_args = list(blueprint_call.find_all('call_argument').map(lambda node: str(node.target) + ':' + str(node.value)))
    assert "template_folder:'templates'" in blueprint_args, \
        "Are you passing the Blueprint instance the correct arguments? There should be a url_prefix keyword argument set to `'/admin'`."

    admin_templates = admin / 'templates'
    assert Path.exists(admin_templates) and Path.is_dir(admin_templates), \
        'Have you created a `templates` folder in the `admin` blueprint folder?'

    move = admin_templates / 'admin'
    assert Path.exists(move) and Path.is_dir(move), \
        'Have you move the `admin` folder from the root `templates` folder to the `admin` blueprint `templates` folder?'

    content      = move / 'content.html'
    content_form = move / 'content_form.html'
    layout       = move / 'layout.html'
    settings     = move / 'settings.html'
    users        = move / 'users.html'
    assert Path.exists(content) and Path.is_file(content), \
        'Is the `content.html` template file in the `cms/admin/templates/admin` folder?'
    assert Path.exists(content_form) and Path.is_file(content_form), \
        'Is the `content_form.html` template file in the `cms/admin/templates/admin` folder?'
    assert Path.exists(layout) and Path.is_file(layout), \
        'Is the `layout.html` template file in the `cms/admin/templates/admin` folder?'
    assert Path.exists(settings) and Path.is_file(settings), \
        'Is the `settings.html` template file in the `cms/admin/templates/admin` folder?'
    assert Path.exists(users) and Path.is_file(users), \
        'Is the `users.html` template file in the `cms/admin/templates/admin` folder?'
