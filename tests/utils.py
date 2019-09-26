import re
from bs4 import BeautifulSoup
from jinja2 import Environment, PackageLoader, exceptions, meta, nodes

env = Environment(loader=PackageLoader('cms', '/admin/templates/admin'))

def template_source(name):
    try:
        return env.loader.get_source(env, name + '.html')[0]
    except exceptions.TemplateNotFound:
        return None

def parsed_content(name):
    return env.parse(template_source(name))

def template_data(name):
    html = ''
    for node in parsed_content(name).find_all(nodes.TemplateData):
        html += node.data
    return BeautifulSoup(html, 'html.parser')

def template_functions(name, function_name):
    functions = []

    for call in parsed_content(name).find_all(nodes.Call):
        if call.node.name == function_name:
            args_string = ''
            if isinstance(call.node, nodes.Name) and isinstance(call.args[0], nodes.Name):
                args_string += call.node.name + ':' + call.args[0].name
            else:
                args = getattr(call, 'args')[0]
                if isinstance(args, nodes.Const):
                    args_string += args.value + ':'
                kwargs = call.kwargs[0] if len(getattr(call, 'kwargs')) > 0 else getattr(call, 'kwargs')
                if isinstance(kwargs, nodes.Keyword):
                    args_string += kwargs.key + ':'
                    if isinstance(kwargs.value, nodes.Const):
                        args_string += kwargs.value.value
                    else:
                        if isinstance(kwargs.value, nodes.Name):
                            args_string += kwargs.value.name
                        else:
                            args_string += kwargs.value.node.name
                            if isinstance(kwargs.value.arg, nodes.Const):
                                args_string += ':' + kwargs.value.arg.value
            functions.append(args_string)

    return functions

def select_code(content, start, end):
    found = False
    code = []

    if isinstance(content, str):
        parsed = parsed_content(content)
    elif isinstance(content, nodes.Node):
        parsed = content
    else:
        return []

    for node in parsed.find_all(nodes.Node):
        if isinstance(node, nodes.TemplateData) and bool(re.search(start, node.data)):
            found = True

        if isinstance(node, nodes.TemplateData) and bool(re.search(end, node.data)):
            found = False

        if found and not isinstance(node, nodes.TemplateData):
                code.append(node)
    return code

def is_for(node):
    if isinstance(node, nodes.For):
        return True
    return False

def dump(main):
    def _dump(node):
        if not isinstance(node, nodes.Node):
            buf.append(node.strip())
            return

        for idx, field in enumerate(node.fields):
            value = getattr(node, field)
            if value == 'load' or value == 'store':
                return
            if idx:
                buf.append('.')
            if isinstance(value, list):
                for idx, item in enumerate(value):
                    if idx:
                        buf.append('.')
                    _dump(item)
            else:
                _dump(value)

    buf = []
    _dump(main)
    # return ''.join(buf)
    return buf