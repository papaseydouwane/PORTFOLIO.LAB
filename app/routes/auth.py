from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db, bcrypt
from app.models import User, Portfolio, Section
from flask_login import login_user, logout_user, current_user, login_required

auth_bp = Blueprint('auth', __name__)

# --- NOUEVELLE PAGE D'ACCUEIL VITRINE ---
@auth_bp.route('/')
def index():
    """Page de présentation de l'application (Landing Page)"""
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    return render_template('public/landing.html') # Nous allons créer ce fichier

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Cet email est déjà utilisé.', 'danger')
            return redirect(url_for('auth.register'))
        
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(email=email, password=hashed_pw)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Compte créé ! Connectez-vous maintenant.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            
            if not user.onboarding_completed:
                return redirect(url_for('auth.onboarding'))
                
            return redirect(url_for('user.dashboard'))
        else:
            flash('Connexion échouée. Vérifiez email et mot de passe.', 'danger')
            
    return render_template('auth/login.html')

@auth_bp.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    if current_user.onboarding_completed:
        return redirect(url_for('user.dashboard'))
        
    if request.method == 'POST':
        profile_type = request.form.get('profile_type') 
        slug = request.form.get('slug').lower().replace(" ", "-")
        
        slug_exists = Portfolio.query.filter_by(slug=slug).first()
        if slug_exists:
            flash('Ce nom de lien est déjà pris.', 'warning')
            return render_template('auth/onboarding.html')

        current_user.profile_type = profile_type
        current_user.onboarding_completed = True
        
        new_portfolio = Portfolio(slug=slug, user_id=current_user.id)
        db.session.add(new_portfolio)
        db.session.flush()

        base_sections = [
            {'type': 'hero', 'content': {'full_name': '', 'title': '', 'bio': ''}},
            {'type': 'formation', 'content': {}},
            {'type': 'experience', 'content': {}},
            {'type': 'projet', 'content': {}},
            {'type': 'langue', 'content': {}},
            {'type': 'certificat', 'content': {}}
        ]

        if profile_type == 'student':
            base_sections.append({'type': 'article', 'content': {}})

        for i, sec in enumerate(base_sections):
            new_section = Section(
                portfolio_id=new_portfolio.id,
                type=sec['type'],
                content=sec['content'],
                position=i
            )
            db.session.add(new_section)
        
        db.session.commit()
        
        flash(f'Bienvenue ! Votre espace {profile_type} a été initialisé.', 'success')
        return redirect(url_for('user.dashboard'))

    return render_template('auth/onboarding.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    # Retour automatique à la landing page au lieu de la page login
    return redirect(url_for('auth.index'))