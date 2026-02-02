from app import create_app, db, bcrypt
from app.models import User
import sys

app = create_app()

def seed_data():
    """Fonction pour initialiser les données critiques (SuperAdmin)"""
    admin_email = "papaseydou.wane@unchk.edu.sn"
    
    admin = User.query.filter_by(email=admin_email).first()
    
    if not admin:
        print(f"--- Création du SuperAdmin : {admin_email} ---")
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
            print("--- SuperAdmin créé avec succès ! ---")
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors du seeding : {e}")
    else:
        print("--- Le SuperAdmin existe déjà. ---")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        seed_data()
        
    app.run(debug=True)