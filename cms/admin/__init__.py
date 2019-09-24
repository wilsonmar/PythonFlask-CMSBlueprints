from flask import Blueprint, redirect, request, url_for, abort, render_template
from cms.admin.models import Type, Content, Setting, User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='templates')

@admin_bp.route('/admin', defaults = {'type': 'page'})
@admin_bp.route('/admin/<type>')
def content(type):
    if requested_type(type):
        content = Content.query.join(Type).filter(Type.name == type)
        return render_template('admin/content.html', type=type, content=content)
    else:
        abort(404)

@admin_bp.route('/admin/create/<type>')
def create(type):
    if requested_type(type):
        types = Type.query.all()
        return render_template('admin/content_form.html', title='Create', types=types, type_name=type)
    else:
        abort(404)

@admin_bp.route('/admin/users')
def users():
    users = User.query.all()
    return render_template('admin/users.html', title='Users', users=users)

@admin_bp.route('/admin/settings')
def settings():
    settings = Setting.query.all()
    return render_template('admin/settings.html', title='Settings', settings=settings)