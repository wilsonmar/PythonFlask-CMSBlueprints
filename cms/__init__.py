from flask import Flask, render_template, abort

from cms.admin import admin_bp
from cms.admin.models import db, Content, Type, Setting, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}/{}'.format(app.root_path, 'content.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.template_filter('pluralize')
def pluralize(string, end=None, rep=''):
    if end and string.endswith(end):
        return string[:-1 * len(end)] + rep
    else:
        return string + 's'

@app.route('/', defaults = {'slug': 'home'})
@app.route('/<slug>')
def index(slug):
    titles = Content.query.with_entities(Content.slug, Content.title).join(Type).filter(Type.name == 'page')
    content = Content.query.filter(Content.slug == slug).first_or_404()
    return render_template('index.html', titles=titles, content=content)

app.register_blueprint(admin_bp)

if __name__ == "__main__":
    app.run(debug=True)