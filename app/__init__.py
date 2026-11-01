"""Flask app factory."""
from flask import Flask, render_template

from .config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    from .routes import bp

    app.register_blueprint(bp)

    @app.errorhandler(404)
    def not_found(_error):
        return render_template(
            "message.html",
            title="Page not found",
            message="That page doesn't exist — let's get you back to the books.",
        ), 404

    return app
