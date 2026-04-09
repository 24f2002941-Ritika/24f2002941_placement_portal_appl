from app import app
from models import db, Admin

with app.app_context():

    db.create_all()

    admin = Admin(username="admin", password="admin123")

    db.session.add(admin)

    db.session.commit()

    print("Database created with admin")