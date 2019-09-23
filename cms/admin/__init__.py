from flask import Blueprint, redirect, request, url_for, abort, render_template
from cms.admin.models import Type, Content, Setting, User


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')