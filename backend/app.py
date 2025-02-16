from flask import Flask
from extensions import db
from models.model import User, Subject, Chapter, Quiz, Question, Score
from auth.routes import auth_bp
from auth.protected_routes import protected_bp  # Import authentication routes

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize Extensions
db.init_app(app)

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(protected_bp, url_prefix='/protected')

# Create the database tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
