"""Initialize app"""
from flask import Flask
from application.extensions import csrf
from flask_wtf.csrf import CSRFProtect

import logging
from flask_simplelogin import SimpleLogin

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    """Construct the core application."""
    app = Flask(__name__,
                instance_relative_config=False)
    app.config.from_object('config.Config')
    app.config['SECRET_KEY'] = '5iRJN07WkpqmqyiSx5c9vsjFJD23YyB5'
    #csrf.init_app(app)
    csrf = CSRFProtect(app)
    csrf.init_app(app)

    ###################can be replaced by another  auth
    def check_user_login(user):
        """:param user: dict {'username': 'foo', 'password': 'bar'}"""

        allowed = False

        if user.get('username') == 'Rafal' and user.get('password') == 'rafal':
            allowed = True
        if user.get('username') == 'Guest' and user.get('password') == 'guest':
            allowed = True
        if user.get('username') == 'Admin' and user.get('password') == 'admin':
            allowed = True

        return allowed

    SimpleLogin(app, check_user_login)
    #######################################################



    with app.app_context():

        # Import main Blueprint
        from . import routes
        app.register_blueprint(routes.main_bp)


        return app