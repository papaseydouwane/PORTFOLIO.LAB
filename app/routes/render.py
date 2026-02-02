from flask import Blueprint, render_template, abort, redirect, url_for
from app.models import Portfolio, Section, User 

render_bp = Blueprint('render', __name__)

@render_bp.route('/u/<slug>')
def view_portfolio(slug):
    portfolio = Portfolio.query.filter_by(slug=slug).first()
    
    if not portfolio:
        abort(404)
        
    if not portfolio.owner.is_active:
        return render_template('errors/suspended.html'), 403


    sections = Section.query.filter_by(portfolio_id=portfolio.id).order_by(Section.position.asc()).all()

    return render_template('public/portfolio_view.html', 
                           portfolio=portfolio, 
                           sections=sections)

@render_bp.route('/portfolio/<slug>/<category>')
def view_category(slug, category):
    portfolio = Portfolio.query.filter_by(slug=slug).first_or_404()
    
    allowed_types = {
        'formations': 'formation',
        'experiences': 'experience',
        'projets': 'projet',
        'recherche': 'article',
        'certifications': 'certificat',
        'langues': 'langue'
    }
    
    if category not in allowed_types:
        return redirect(url_for('render.view_portfolio', slug=slug))
    
    db_type = allowed_types[category]
    sections = Section.query.filter_by(
        portfolio_id=portfolio.id, 
        type=db_type
    ).order_by(Section.position.asc()).all()
    
    return render_template('public/category_view.html', 
                           portfolio=portfolio, 
                           sections=sections, 
                           category_name=category)
    

@render_bp.route('/expertise/<slug>')
def expertise(slug):
    portfolio = Portfolio.query.filter_by(slug=slug).first_or_404()
    # Récupérer TOUTES les sections pour être sûr
    sections = Section.query.filter_by(portfolio_id=portfolio.id).all()
    
    # Vérification dans la console (terminal)
    print(f"DEBUG: Portfolio ID {portfolio.id} a {len(sections)} sections")
    
    return render_template('public/rechercheeteducation.html', 
                           portfolio=portfolio, 
                           sections=sections)