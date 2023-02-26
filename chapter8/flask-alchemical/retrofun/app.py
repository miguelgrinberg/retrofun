from flask import Flask
from .models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    db.init_app(app)

    from .routes import bp
    app.register_blueprint(bp)

    return app
