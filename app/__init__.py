from flask import Flask
import os
from config import Connection

def create_app():
    app = Flask(__name__, instance_relative_config=True, static_folder='static', template_folder='templates')

    # Configurations can be set here, e.g., from a config file
    app.config.from_object(Connection)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register Blueprints here
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app
