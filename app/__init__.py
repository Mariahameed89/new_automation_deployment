from flask_migrate import Migrate
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize the app and db
db = SQLAlchemy()
migrate = Migrate()  # Initialize Flask-Migrate

def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'))
    app.config['SECRET_KEY'] = '434c29b387cb5f2b1f0694d7374865fe92c277150dcd8b24'

    # Configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'  # Database file path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)  # Bind Flask-Migrate to the app and SQLAlchemy

    # Import and register blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # Create the database tables if they don't exist
    with app.app_context():
        db.create_all()

    return app
