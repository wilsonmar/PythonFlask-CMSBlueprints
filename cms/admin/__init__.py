from flask import Flask, render_template, abort, Blueprint
from cms.admin.models import Content, Setting, Type, User

admin_bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='templates')

def requested_type(type):
    types = [row.name for row in Type.query.all()]
    return True if type in types else False

@admin_bp.route('/', defaults = {'type': 'page'})
@admin_bp.route('/<type>')
def content(type):
    if requested_type(type):
        content = Content.query.join(Type).filter(Type.name == type)
        return render_template('admin/content.html', type=type, content=content)
    else:
        abort(404)

@admin_bp.route('/admin/create/<type>', methods=("GET", "POST"))
def create(type):
    if requested_type(type):
        # -----------------------------------
        # if request.method == 'POST':
        #     title = request.form['title']
        #     slug = request.form['slug']
        #     type_id = request.form['type_id']
        #     body = request.form['body']
        #     error = None

        #     if not title: 
        #         error = 'The title is required.'
        #     elif not type:
        #         error = 'The type is required.'

        #     if error is None:
        #         content = Content(title=title, slug=slug, type_id=type_id, body=body)
        #         db.session.add(content)
        #         db.session.commit()
        #         return redirect(url_for('content', type=type))

        #     flash(error)
        # -----------------------------------
        types = Type.query.all()
        return render_template('admin/content_form.html', title='Create', types=types, type_name=type)
    else:
        abort(404)

# # ----------------------------
# @admin_bp.route('/admin/edit/<id>', methods=('GET', 'POST'))
# def edit(id):
#     content = Content.query.get_or_404(id)
#     type = Type.query.get(request.form['type_id'])

#     if request.method == 'POST':
#         content.title = request.form['title']
#         content.slug = request.form['slug']
#         content.type_id = request.form['type_id']
#         content.body = request.form['body']
#         content.updated_at = datetime.utcnow()
#         error = None

#         if not request.form['title']:
#             error = 'The title is required.'

#         if error is None:
#             db.session.commit()
#             return redirect(url_for('content', type=type.name))

#         flash(error)

#     types = Type.query.all()
#     return render_template('admin/content_form.html',
#         types=types, title='Edit', item_title=content.title,
#         slug=content.slug, type_name=type.name, type_id=content.type_id, body=content.body)
# # ----------------------------

@admin_bp.route('/admin/users')
def users():
    users = User.query.all()
    return render_template('admin/users.html', title='Users', users=users)

@admin_bp.route('/admin/settings')
def settings():
    settings = Setting.query.all()
    return render_template('admin/settings.html', title='Settings', settings=settings)