# Verify Local Environment

## Windows
Open a command prompt or powershell and run the following commands, replacing 'project-root' with the path to the root folder of the Project.

```
> cd 'project-root'
> python -m venv venv
> venv\Scripts\activate.bat
> pip install -r requirements.txt
```

## macOS
Open a terminal and run the following commands, replacing 'project-root' with the path to the root folder of the Project.

```
$ cd 'project-root'
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

*Note: If you've installed Python 3 using a method other than Homebrew, you might need to type `python` in the second command instead of `python3`.*

## About pip Versions
`pip` updates frequently, but versions greater than `19.x.x` should work with this project.

## Verify Setup
In order to verify that everything is setup correctly, run the following command from the project root.

```
pytest
```

You should see that all the tests are failing. This is good! We’ll be fixing these tests once we jump into the build step.

Every time you want to check your work locally you can type that command, and it will report the status of every task in the project.

## Previewing Your Work
You can preview your work by running `flask run` in the root of your Project. Then visit `http://localhost:5000` in your browser.

# Module 01 - Admin Blueprint

## 1.1 - Folder Structure

@pytest.mark.test_folder_structure_module1
module_file

## 1.2 - Models File

@pytest.mark.test_models_file_module1
import_sqlalchemy

## 1.3 - Move Models

@pytest.mark.test_move_models_module1

## 1.4 - Import Instance & Models

@pytest.mark.test_import_models_module1
init_app

## 1.5 - Create a Blueprint

@pytest.mark.test_create_blueprint_module1

## 1.6 - Move Routes

@pytest.mark.test_move_routes_module1

## 1.7 - Register Blueprint & Revise Templates

@pytest.mark.test_register_blueprint_module1

## 1.8 - Template Folder

@pytest.mark.test_template_folder_module1

# Module 02 - Create Form

## 2.1 - Add Form Controls

@pytest.mark.test_add_from_controls_module2

## 2.2 - Adjust Create Route

@pytest.mark.test_adjust_create_route_data_module2

## 2.3 - Create Form Data

@pytest.mark.test_form_data_module2

## 2.4 - Validate Data

@pytest.mark.test_validate_route_module2

## 2.5 - Add Data

@pytest.mark.test_add_data_module2

## 2.6 - Add Edit Route

@pytest.mark.test_add_edit_route_module2

## 2.7 - Populate Form Controls

@pytest.mark.test_populate_form_controls_module2

## 2.8 - Edit Form Data

@pytest.mark.test_edit_form_data_module2

## 2.9 - Validate Data

@pytest.mark.test_validate_edit_data_module2

## 2.10 - Update Data

@pytest.mark.test_update_data_module2
