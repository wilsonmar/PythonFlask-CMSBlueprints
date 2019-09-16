from datetime import datetime

from flask import Flask, render_template, redirect, request, url_for, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/{}'.format(app.root_path, 'content.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'), nullable=False)
    type = db.relationship('Type', backref=db.backref('Content', lazy=True))
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(100), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    firstname = db.Column(db.String(100), unique=True, nullable=False)
    lastname = db.Column(db.String(100), unique=True, nullable=False)

@app.template_filter('pluralize')
def pluralize(string, end=None, rep=''):
    if end and string.endswith(end):
        return string[:-1 * len(end)] + rep
    else:
        return string + 's'

def requested_type(type):
    types = [row.name for row in Type.query.all()]
    return True if type in types else False

homepage = Setting.query.filter(Setting.key == 'homepage').first().value

@app.route('/', defaults = {'slug': homepage})
@app.route('/<slug>')
def index(slug):
    titles = Content.query.with_entities(Content.slug, Content.title).join(Type).filter(Type.name == 'page')
    content = Content.query.filter(Content.slug == slug).first_or_404()
    return render_template('index.html', titles=titles, content=content)

@app.route('/admin', defaults = {'type': 'page'})
@app.route('/admin/<type>')
def content(type):
    if requested_type(type):
        content = Content.query.join(Type).filter(Type.name == type)
        return render_template('admin/content.html', type=type, content=content)
    else:
        abort(404)

@app.route('/admin/users')
def users():
    users = User.query.all()
    return render_template('admin/users.html', title='Users', users=users)

@app.route('/admin/settings')
def settings():
    settings = Setting.query.all()
    return render_template('admin/settings.html', title='Settings', settings=settings)

@app.route('/admin/create/<type>', methods=('GET', 'POST'))
def create(type):
    if requested_type(type):
        if request.method == "POST":
            title = request.form["title"]
            slug = request.form["slug"]
            type_id = request.form["type_id"]
            body = request.form["body"]
            error = None

            if not title:
                error = 'The title is required.'
            elif not type:
                error = 'The type is required.'

            if error is None:
                content = Content(title=title, slug=slug, type_id=type_id, body=body)
                db.session.add(content)
                db.session.commit()
                return redirect(url_for('content', type=type))

            flash(error)

        types = Type.query.all()
        return render_template('admin/content_form.html', title='Create', types=types, type_name=type)
    elif type == 'user':
        if request.method == "POST":
            firstname = request.form["firstname"]
            lastname = request.form["lastname"]
            username = request.form["username"]
            email = request.form["email"]
            error = None

            if not username:
                error = 'username is required.'

            if error is None:
                user = User(firstname=firstname, lastname=lastname, username=username, email=email)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('users'))

            flash(error)

        return render_template('admin/user_form.html')
    elif type == 'setting':
        if request.method == "POST":
            key = request.form["key"]
            value = request.form["value"]
            error = None

            if not key:
                error = 'Key is required.'
            if not value:
                error = 'Value is required.'

            if error is None:
                user = Setting(key=key, value=value)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('settings'))

            flash(error)

        return render_template('admin/setting_form.html')
    else:
        abort(404)

@app.route('/admin/edit/<id>', methods=('GET', 'POST'))
def edit(id):
    content = Content.query.get_or_404(id)
    type = Type.query.get(request.form["type_id"])

    if request.method == "POST":
        content.title = request.form["title"]
        content.slug = request.form["slug"]
        content.type_id = request.form["type_id"]
        content.body = request.form["body"]
        content.updated_at = datetime.utcnow()
        error = None

        if not request.form["title"]:
            error = 'The title is required.'

        if error is None:
            db.session.commit()
            return redirect(url_for('content', type=type.name))

        flash(error)

    types = Type.query.all()
    return render_template('admin/content_form.html',
        types=types, title='Edit', item_title=content.title,
        slug=content.slug, type_name=type.name, type_id=content.type_id, body=content.body)

@app.route('/admin/edit/setting/<id>', methods=('GET', 'POST'))
def edit_setting(id):
    setting = Setting.query.get_or_404(id)

    if request.method == "POST":
        setting.key = request.form["key"]
        setting.value = request.form["value"]
        error = None

        if not setting.key:
            error = 'Key is required.'
        if not setting.value:
            error = 'Value is required.'

        if error is None:
            db.session.commit()
            return redirect(url_for('settings'))

        flash(error)

    types = Type.query.all()
    return render_template('admin/setting_form.html', key=setting.key,  value=setting.value)

@app.route('/admin/edit/user/<id>', methods=('GET', 'POST'))
def edit_user(id):
    user = User.query.get_or_404(id)

    if request.method == "POST":
        user.firstname = request.form["firstname"]
        user.lastname = request.form["lastname"]
        user.username = request.form["username"]
        user.email = request.form["email"]
        error = None

        if not request.form["title"]:
            error = 'The title is required.'

        if error is None:
            db.session.commit()
            return redirect(url_for('settings'))

        flash(error)

    types = Type.query.all()
    return render_template('admin/user_form.html',
        title='Edit', firstname=user.firstname,
        lastname=user.lastname, username=user.username, email=user.email)

if __name__ == "__main__":
    app.run(debug=True)