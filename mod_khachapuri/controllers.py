from flask import Blueprint, render_template, send_from_directory, abort, current_app
from app import testing_site
import os
import markdown
import codecs
import json

mod_khachapuri = Blueprint("khachapuri", __name__)

if testing_site == "KHACHAPURI":
    _host = "localhost:5000"
else:
    _host = "the-yelp-of-khachapuri.site"


@mod_khachapuri.route("/favicon.ico", host=_host)
def favicon():
    return send_from_directory(
        os.path.join(current_app.root_path, "static"),
        "favicon_khachapuri.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@mod_khachapuri.route("/css/<path:css>", host=_host)
def css(css):
    if "fonts" in css:
        return send_from_directory(
            os.path.join(current_app.root_path, "static/css"), css
        )
    else:
        return send_from_directory(
            os.path.join(current_app.root_path, "static/gen"), css
        )


@mod_khachapuri.route("/images/<folder>/<image>", host=_host)
def image_with_folder(folder, image):
    return send_from_directory(
        os.path.join(current_app.root_path, "static/images", folder), image
    )


@mod_khachapuri.route("/images/<image>", host=_host)
def image(image):
    return send_from_directory(
        os.path.join(current_app.root_path, "static/images"), image
    )


@mod_khachapuri.route("/", methods=["GET"], host=_host)
def index():
    page = "khachapuri/index.md"
    html = get_html(page)
    return render_template(
        "khachapuri/post.html", html=html, t="the yelp of khachapuri"
    )


@mod_khachapuri.route("/downloads/<doc>", methods=["GET"], host=_host)
def download(doc):
    return send_from_directory("files", doc)


@mod_khachapuri.route(
    "/reviews",
    methods=["GET"],
    host=_host,
    defaults={"filter_value": None, "filter_type": None},
)
@mod_khachapuri.route(
    "/reviews/<filter_type>/<filter_value>", methods=["GET"], host=_host
)
def reviews(filter_type, filter_value):
    filepath = os.path.join(
        current_app.root_path, "templates", "khachapuri", "reviews.json"
    )
    input_file = codecs.open(filepath, mode="r", encoding="utf-8")
    reviews = json.loads(input_file.read())["reviews"]

    unique_countries = set([r["country"] for r in reviews])
    unique_types = set([r["type"] for r in reviews])
    if filter_type:
        reviews = [r for r in reviews if str(r[filter_type]).lower() == filter_value]
    return render_template(
        "khachapuri/reviews.html",
        reviews=reviews,
        unique_countries=unique_countries,
        unique_types=unique_types,
        t="reviews – the yelp of khachapuri",
    )


@mod_khachapuri.route(
    "/bounties",
    methods=["GET"],
    host=_host,
    defaults={"filter_value": None, "filter_type": None},
)
@mod_khachapuri.route(
    "/bounties/<filter_type>/<filter_value>", methods=["GET"], host=_host
)
def bounties(filter_type, filter_value):
    filepath = os.path.join(
        current_app.root_path, "templates", "khachapuri", "bounties.json"
    )
    input_file = codecs.open(filepath, mode="r", encoding="utf-8")
    bounties = json.loads(input_file.read())["bounties"]

    unique_countries = set([b["country"] for b in bounties])
    open_bounties = [
        b for b in bounties if not b.get("fulfilled") and not b.get("closed")
    ]
    fulfilled_bounties = [b for b in bounties if b.get("fulfilled")]
    if filter_type:
        open_bounties = [
            b for b in open_bounties if str(b[filter_type]).lower() == filter_value
        ]
        fulfilled_bounties = [
            b for b in fulfilled_bounties if str(b[filter_type]).lower() == filter_value
        ]
    return render_template(
        "khachapuri/bounties.html",
        open_bounties=open_bounties,
        fulfilled_bounties=fulfilled_bounties,
        unique_countries=unique_countries,
        t="bounties – the yelp of khachapuri",
    )


@mod_khachapuri.route("/<title>", methods=["GET"], host=_host)
def page(title):
    page = "khachapuri/%s.md" % title
    html = get_html(page)
    if html == "<p>404</p>":
        return abort(404)
    return render_template(
        "khachapuri/post.html",
        html=html,
        t="{0} – the yelp of khachapuri".format(title),
    )


def get_html(page):
    filepath = os.path.join(current_app.root_path, "templates", page)
    try:
        input_file = codecs.open(filepath, mode="r", encoding="utf-8")
        text = input_file.read()
    except:
        text = "404"
    return markdown.markdown(
        text,
        extensions=[
            "markdown.extensions.nl2br",
            "markdown.extensions.toc",
            "markdown.extensions.tables",
            "markdown.extensions.def_list",
            "markdown.extensions.abbr",
            "markdown.extensions.footnotes",
        ],
    )
