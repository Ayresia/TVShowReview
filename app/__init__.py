from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    from app.database import init_db
    init_db(app)

    from .show import show as show_blueprint
    app.register_blueprint(show_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
