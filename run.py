from app import create_app, db, bcrypt
from app.models import User
import os

app = create_app()

def seed_data():
    """Initialise le SuperAdmin si absent"""
    admin_email = "papaseydou.wane@unchk.edu.sn"
    with app.app_context():
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            hashed_password = bcrypt.generate_password_hash("Qqmkl@8345").decode('utf-8')
            super_admin = User(
                email=admin_email,
                password=hashed_password,
                is_admin=True,          
                profile_type="admin",    
                onboarding_completed=True 
            )
            db.session.add(super_admin)
            try:
                db.session.commit()
                print("SuperAdmin créé.")
            except Exception:
                db.session.rollback()

# Pour Vercel : On expose l'objet app globalement
# On ne lance db.create_all() qu'une seule fois au chargement du module
with app.app_context():
    from app.models import User # Import important ici
    db.create_all()
    print("Base de données initialisée !")

if __name__ == "__main__":
    # Ce bloc ne s'exécute qu'en LOCAL
    app.run(debug=True)
