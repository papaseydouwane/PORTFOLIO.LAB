from flask import Blueprint, render_template
from flask_login import login_required
from app.decorators import admin_required
from app.models import User, Portfolio

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    users = User.query.all()
    portfolios_count = Portfolio.query.count()
    return render_template('admin/index.html', users=users, count=portfolios_count)