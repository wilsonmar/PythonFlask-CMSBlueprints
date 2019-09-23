from flask import Flask

from cms.admin.models import db, Content, Type, Setting, User

app = Flask(__name__)

db.init_app(app)