from flask import Blueprint, render_template, send_from_directory, abort, current_app
from app import testing_site
import os
import markdown
import codecs

mod_corbin = Blueprint("corbin", __name__)

if testing_site == "CORBIN":
    _host = "localhost:5000"
else:
    _host = "corbindewitt.com"


@mod_corbin.route("/favicon.ico", host=_host)
def favicon():
    # return send_from_directory(os.path.join(current_app.root_path, 'static'),
    #                            'favicon_corbin.ico', mimetype='image/vnd.microsoft.icon')
    return send_from_directory(
        os.path.join(current_app.root_path, "static"),
        "favicon_corbin-4-small.png",
        mimetype="image/png",
    )


@mod_corbin.route("/css/<path:css>", host=_host)
def css(css):
    if "fonts" in css:
        return send_from_directory(
            os.path.join(current_app.root_path, "static/css"), css
        )
    else:
        return send_from_directory(
            os.path.join(current_app.root_path, "static/gen"), css
        )


@mod_corbin.route("/images/<folder>/<image>", host=_host)
def image_with_folder(folder, image):
    return send_from_directory(
        os.path.join(current_app.root_path, "static/images", folder), image
    )


@mod_corbin.route("/images/<image>", host=_host)
def image(image):
    return send_from_directory(
        os.path.join(current_app.root_path, "static/images"), image
    )


@mod_corbin.route("/", methods=["GET"], host=_host)
def index():
    page = "corbin/index.md"
    html = get_html(page)
    return render_template("corbin/post.html", html=html, t="corbin dewitt")


@mod_corbin.route("/downloads/<doc>", methods=["GET"], host=_host)
def download(doc):
    return send_from_directory("files", doc)


@mod_corbin.route("/<title>", methods=["GET"], host=_host)
def page(title):
    page = "corbin/%s.md" % title
    html = get_html(page)
    if html == "<p>404</p>":
        return abort(404)
    return render_template(
        "corbin/post.html", html=html, t="{0} – corbin dewitt".format(title)
    )


def get_html(page):
    filepath = os.path.join(current_app.root_path, "templates", page)
    try:
        input_file = codecs.open(filepath, mode="r", encoding="utf-8")
        text = input_file.read()
    except:
        text = "404"
    return markdown.markdown(text)
