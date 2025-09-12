from flask import Flask
import os
from config import Config
from flask_pymongo import PyMongo

mongo = PyMongo()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Configurations can be set here, e.g., from a config file
    app.config.from_object(Config)

    # Initialize PyMongo
    mongo.init_app(app)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register Blueprints here
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
