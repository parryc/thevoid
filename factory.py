from database import db
from flask import Flask


def create_app(name=__name__):
    app = Flask(
        name,
        host_matching=True,
        static_host="/static",
    )
    app.config.from_object("config.DevelopmentConfig")
    db.init_app(app)
    return app
