from app import db
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app import login_manager 

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    

    profile_type = db.Column(db.String(50), nullable=True) 
    onboarding_completed = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    portfolio = db.relationship('Portfolio', backref='owner', uselist=False, cascade="all, delete-orphan")

class Portfolio(db.Model):
    __tablename__ = 'portfolios'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    slug = db.Column(db.String(80), unique=True, nullable=False)
    

    theme_config = db.Column(JSONB, default=lambda: {
        "primary_color": "#3B82F6", 
        "secondary_color": "#1F2937",
        "font": "sans"
    }) 
    
    sections = db.relationship('Section', backref='portfolio', order_by="Section.position", cascade="all, delete-orphan")
    is_published = db.Column(db.Boolean, default=True)
    
class Section(db.Model):
    __tablename__ = 'sections'
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False)

    type = db.Column(db.String(50), nullable=False) 
    
    title = db.Column(db.String(100))
    

    content = db.Column(JSONB, nullable=False)      
    
    position = db.Column(db.Integer, default=0)
    is_visible = db.Column(db.Boolean, default=True)

class SectionTemplate(db.Model):
    __tablename__ = 'section_templates'
    id = db.Column(db.Integer, primary_key=True)
    profile_target = db.Column(db.String(50)) 
    section_type = db.Column(db.String(50))
    default_content = db.Column(JSONB)
    default_position = db.Column(db.Integer)
    

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))