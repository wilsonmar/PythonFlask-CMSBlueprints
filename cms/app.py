import os

from datetime import datetime

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
BASE_DIRECTORY = os.path.abspath(os.getcwd())
FILE_PATH = os.path.join(BASE_DIRECTORY, 'db', 'cms.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(FILE_PATH)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'), nullable=False)
    type = db.relationship('Type', backref=db.backref('Content', lazy=True))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('Content', lazy=True))

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

homepage = Setting.query.filter(Setting.key == 'homepage').first().value

@app.route('/', defaults = {'slug': homepage})
@app.route('/<slug>')
def index(slug):
    titles = Content.query.with_entities(Content.slug, Content.title).join(Type).filter(Type.name == 'page')
    content = Content.query.filter(Content.slug == slug).first_or_404()
    return render_template('index.html', titles = titles, content = content)

@app.route('/admin')
@app.route('/admin/pages')
def pages():
    items = Content.query.join(Type).filter(Type.name == 'page')
    return render_template('admin/content.html', title='Pages', items=items)

@app.route('/admin/posts')
def posts():
    items = Content.query.join(Type).filter(Type.name == 'post')
    return render_template('admin/content.html', title='Posts', items=items)

@app.route('/admin/partials')
def partials():
    items = Content.query.join(Type).filter(Type.name == 'partial')
    return render_template('admin/content.html', title='Partials', items=items)

@app.route('/admin/templates')
def templates():
    items = Content.query.join(Type).filter(Type.name == 'template')
    return render_template('admin/content.html', title='Templates', items=items)

@app.route('/admin/edit/<id>')
def edit(id):
    item = Content.query.get(id)
    types = Type.query.all()
    categories = Category.query.all()
    return render_template('admin/content_form.html', title='Edit', item=item, types=types, categories=categories)

@app.route('/admin/create')
def create():
    item = { 'id': '', 'title': '', 'slug': '' }
    types = Type.query.all()
    categories = Category.query.all()
    return render_template('admin/content_form.html', title='Edit', item=item, types=types, categories=categories)

@app.route('/admin/users')
def users():
    users = User.query.all()
    return render_template('admin/users.html', title='Users', users=users)

@app.route('/admin/settings')
def settings():
    settings = Setting.query.all()
    return render_template('admin/settings.html', title='Settings', settings=settings)

if __name__ == "__main__":
    app.run(debug=True)
