from flask import Flask

from cms.admin.models import db

app = Flask(__name__)

db.init_app(app)