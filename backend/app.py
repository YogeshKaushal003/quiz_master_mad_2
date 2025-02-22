from flask import Flask
from extensions import db
from models.model import User, Subject, Chapter, Quiz, Question, Score
from auth.routes import auth_bp
from admin.routes import admin_bp
from auth.protected_routes import protected_bp  # Import authentication routes
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize Extensions
db.init_app(app)
migrate = Migrate(app, db)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(protected_bp, url_prefix='/protected')
app.register_blueprint(admin_bp, url_prefix='/admin')


# Create the database tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
