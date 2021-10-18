from flask import Flask, render_template, request, send_from_directory
from flask_assets import Environment, Bundle
from flask_compress import Compress
from database import db
from factory import create_app
from werkzeug.routing import BaseConverter

app = create_app(__name__)
app.config.from_object("config.DevelopmentConfig")
assets = Environment(app)
Compress(app)

testing_site = app.config["TESTING_SITE"]


class HostConverter(BaseConverter):
    app = None
    test_map = {
        "LEFLAN": "leflan.eu",
        "PARRYC": "parryc.com",
        "CORBIN": "corbindewitt.com",
        "KHACHAPURI": "the-yelp-of-khachapuri.site",
        "AVAR": "avar.rocks",
        "ZMNEBI": "zmnebi.com",
    }

    def __init__(
        self,
        map,
        site="",
    ):
        super().__init__(map)
        self.site = site

    def to_python(self, value):
        return value

    def to_url(self, value):
        with app.app_context():
            testing = app.config[f"{self.site}_TEST"]
            if not testing:
                host = self.test_map[self.site]
            else:
                host = "localhost:5000"
            return host


def circle_num_from_jinja_loop(num):
    return "①②③④⑤⑥⑦⑧⑨⑩"[num - 1]


def taste(taste_rating):
    return int(taste_rating) * "💛"


def price(price_rating):
    return int(price_rating) * "💰"


app.jinja_env.filters["circle_num"] = circle_num_from_jinja_loop
app.jinja_env.filters["taste"] = taste
app.jinja_env.filters["price"] = price

# clear the automatically added route for static
# https://github.com/mitsuhiko/flask/issues/1559
# enable host matching and re-add the static route with the desired host
# app.add_url_rule(
#     app.static_url_path + "/<path:filename>",
#     endpoint="static",
#     view_func=app.send_static_file,
# )


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.after_request
def add_header(response):
    # set cache to 2 weeks
    response.cache_control.max_age = 1209600
    return response


# Define static asset bundles to be minimized and deployed
bundles = {
    "parryc_css": Bundle(
        "css/marx.min.css",
        "css/style_parryc.css",
        "css/fonts/ptsans/fonts.css",
        filters="cssmin",
        output="gen/parryc.css",
    ),
    "khachapuri_css": Bundle(
        "css/marx.min.css",
        "css/style_khachapuri.css",
        "css/fonts/ptsans/fonts.css",
        filters="cssmin",
        output="gen/khachapuri.css",
    ),
    "corbin_css": Bundle(
        "css/marx.min.css",
        "css/style_corbin.css",
        "css/fonts/cormorant/fonts.css",
        filters="cssmin",
        output="gen/corbin.css",
    ),
    "leflan_css": Bundle(
        "css/marx.min.css",
        "css/style_leflan.css",
        "css/fonts/source-code-pro/source-code-pro.css",
        "css/fonts/cmu/fonts.css",
        "css/fonts/bpg-ingiri/bpg-ingiri.css",
        "css/fonts/mayan/fonts.css",
        filters="cssmin",
        output="gen/leflan.css",
    ),
}
assets.register(bundles)

# Import a module / component using its blueprint handler variable
from mod_parryc.controllers import mod_parryc

app.register_blueprint(mod_parryc)
from mod_leflan.controllers import mod_leflan

app.register_blueprint(mod_leflan)
# from mod_corbin.controllers import mod_corbin
#
# app.register_blueprint(mod_corbin)
# from mod_khachapuri.controllers import mod_khachapuri
#
# app.register_blueprint(mod_khachapuri)
# from avar_rocks.flask.controllers import mod_avar
#
# app.register_blueprint(mod_avar)
from mod_zmnebi.controllers import mod_zmnebi

app.register_blueprint(mod_zmnebi)
