from flask import render_template
from flask_assets import Environment, Bundle
from flask_compress import Compress
from factory import create_app

app = create_app(__name__)
app.config.from_object("config.DevelopmentConfig")
assets = Environment(app)
Compress(app)
testing_site = app.config["TESTING_SITE"]


def circle_num_from_jinja_loop(num):
    return "①②③④⑤⑥⑦⑧⑨⑩"[num - 1]


def taste(taste_rating):
    return int(taste_rating) * "💛"


def price(price_rating):
    return int(price_rating) * "💰"


app.jinja_env.filters["circle_num"] = circle_num_from_jinja_loop
app.jinja_env.filters["taste"] = taste
app.jinja_env.filters["price"] = price


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.after_request
def add_header(response):
    # set cache to 1 year
    response.cache_control.max_age = 31536000
    response.cache_control.public = True
    return response


# Define static asset bundles to be minimized and deployed
bundles = {
    "parryc_css": Bundle(
        "css/marx.min.css",
        "css/style_parryc.css",
        "css/fonts/ptsans/fonts.css",
        "css/fonts/source-code-pro/source-code-pro.css",
        "css/fonts/cmu/fonts.css",
        "css/fonts/bpg-ingiri/bpg-ingiri.css",
        "css/fonts/mayan/fonts.css",
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
    "bookarts_css": Bundle(
        "css/marx.min.css",
        "css/style_bookarts.css",
        "css/fonts/bookarts/fonts.css",
        filters="cssmin",
        output="gen/bookarts.css",
    ),
}
assets.register(bundles)

from mod_parryc.controllers import mod_parryc

app.register_blueprint(mod_parryc)
from mod_leflan.controllers import mod_leflan

app.register_blueprint(mod_leflan)
from mod_corbin.controllers import mod_corbin

app.register_blueprint(mod_corbin)
from mod_khachapuri.controllers import mod_khachapuri

app.register_blueprint(mod_khachapuri)
from avar_rocks.flask.controllers import mod_avar

app.register_blueprint(mod_avar)
from mod_zmnebi.controllers import mod_zmnebi

app.register_blueprint(mod_zmnebi)
from mod_bookarts.controllers import mod_bookarts

app.register_blueprint(mod_bookarts)
