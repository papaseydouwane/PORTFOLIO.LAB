from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from app import db
from app.models import User, Portfolio, Section
from flask_login import login_required, current_user

user_bp = Blueprint('user', __name__)

# --- 1. LE COCKPIT (RÉSUMÉ & STATISTIQUES) ---
@user_bp.route('/')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))

    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    
    if not portfolio:
        return redirect(url_for('auth.onboarding'))
        
    stats = {
        'sections_count': Section.query.filter_by(portfolio_id=portfolio.id).count(),
        'is_published': getattr(portfolio, 'is_published', True)
    }
        
    return render_template('dashboard/index.html', portfolio=portfolio, stats=stats)

# --- 2. LOGIQUE D'ÉDITION CENTRALISÉE ---

def get_sections_and_render(db_type, template):
    """
    Récupère les sections d'un type précis et les injecte dans le template.
    Cette fonction évite la redondance de code pour chaque catégorie.
    """
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first_or_404()
    sections = Section.query.filter_by(
        portfolio_id=portfolio.id, 
        type=db_type
    ).order_by(Section.position.asc()).all()
    return render_template(template, portfolio=portfolio, sections=sections)

@user_bp.route('/edit/entete')
@login_required
def edit_entete():
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first_or_404()
    section = Section.query.filter_by(portfolio_id=portfolio.id, type='hero').first()
    
    # Création automatique de la section Hero si elle n'existe pas
    if not section:
        section = Section(portfolio_id=portfolio.id, type='hero', content={}, position=0)
        db.session.add(section)
        db.session.commit()
        
    return render_template('dashboard/entete.html', portfolio=portfolio, section=section)

@user_bp.route('/edit/formations')
@login_required
def edit_formations():
    return get_sections_and_render('formation', 'dashboard/formations.html')

@user_bp.route('/edit/experiences')
@login_required
def edit_experiences():
    return get_sections_and_render('experience', 'dashboard/experiences.html')

@user_bp.route('/edit/projets')
@login_required
def edit_projets():
    return get_sections_and_render('projet', 'dashboard/projets.html')

@user_bp.route('/edit/certificats')
@login_required
def edit_certificats():
    return get_sections_and_render('certificat', 'dashboard/certificats.html')

@user_bp.route('/edit/articles')
@login_required
def edit_articles():
    return get_sections_and_render('article', 'dashboard/articlescientifiques.html')

@user_bp.route('/edit/langues')
@login_required
def edit_langues():
    return get_sections_and_render('langue', 'dashboard/langues.html')

# --- 3. ACTIONS DE GESTION DES DONNÉES (CRUD) ---

@user_bp.route('/section/add/<string:section_type>', methods=['POST'])
@login_required
def add_section(section_type):
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first_or_404()
    
    # Calcul de la position suivante pour l'affichage
    last_sec = Section.query.filter_by(portfolio_id=portfolio.id).order_by(Section.position.desc()).first()
    new_pos = (last_sec.position + 1) if last_sec else 0
    
    new_section = Section(
        portfolio_id=portfolio.id,
        type=section_type,
        content={}, 
        position=new_pos
    )
    
    db.session.add(new_section)
    db.session.commit()
    
    flash('Nouvel élément ajouté avec succès.', 'success')
    return redirect(request.referrer)

@user_bp.route('/section/update/<int:section_id>', methods=['POST'])
@login_required
def update_section(section_id):
    section = Section.query.get_or_404(section_id)
    
    if section.portfolio.user_id != current_user.id:
        return jsonify({"error": "Action non autorisée"}), 403
    
    # Fusion des données du formulaire dans le champ JSON content
    data = request.form.to_dict()
    
    # On utilise une copie pour s'assurer que SQLAlchemy détecte la mutation du dictionnaire
    current_content = section.content.copy() if section.content else {}
    current_content.update(data)
    section.content = current_content
    
    db.session.add(section) 
    db.session.commit()
    
    flash('Modifications enregistrées ! ✨', 'success')
    return redirect(request.referrer)

@user_bp.route('/section/delete/<int:section_id>')
@login_required
def delete_section(section_id):
    section = Section.query.get_or_404(section_id)
    if section.portfolio.user_id == current_user.id:
        db.session.delete(section)
        db.session.commit()
        flash('Élément supprimé.', 'info')
    return redirect(request.referrer)

# --- 4. STUDIO DE DESIGN & IDENTITÉ VISUELLE ---

@user_bp.route('/edit/design')
@login_required
def edit_design():
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first_or_404()
    return render_template('dashboard/designcouleurs.html', portfolio=portfolio)

@user_bp.route('/settings/design', methods=['POST'])
@login_required
def update_design():
    """
    Met à jour la configuration visuelle du portfolio.
    Récupère les nouvelles options : Mode de fond, Navigation, Couleurs, etc.
    """
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first_or_404()
    
    new_config = portfolio.theme_config.copy() if portfolio.theme_config else {}
    

    new_config['bg_mode'] = request.form.get('bg_mode', 'dark')
    
    new_config['primary_color'] = request.form.get('primary_color', '#6366F1')

    new_config['nav_style'] = request.form.get('nav_style', 'floating')
    
    new_config['card_style'] = request.form.get('card_style', 'glass')
    new_config['show_grain'] = 'show_grain' in request.form 
    

    if 'text_animation' in request.form:
        new_config['text_animation'] = request.form.get('text_animation')
    
    portfolio.theme_config = new_config
    db.session.commit()
    
    flash('L\'identité visuelle a été mise à jour avec succès ! 🎨', 'success')
    
    return redirect(url_for('user.edit_design'))


@user_bp.route('/section/reorder', methods=['POST'])
@login_required
def reorder_sections():
    """Endpoint pour réorganiser les sections via AJAX"""
    order = request.json.get('order') 
    for index, s_id in enumerate(order):
        section = Section.query.get(s_id)
        if section and section.portfolio.user_id == current_user.id:
            section.position = index
    db.session.commit()
    return jsonify({"status": "success"}), 200