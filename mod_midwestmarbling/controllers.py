from flask import (
    Blueprint,
    render_template,
    send_from_directory,
    abort,
    current_app,
)

from app import testing_site
import os
import markdown
import codecs

mod_midwestmarbling = Blueprint("midwestmarbling", __name__)

if testing_site == "MIDWESTMARBLING":
    _host = "localhost:5000"
else:
    _host = "midwestmarbling.art"


def _t(title):
    return f"{title}"


@mod_midwestmarbling.route("/favicon.ico", host=_host)
def favicon():
    return send_from_directory(
        os.path.join(current_app.root_path, "static"),
        "favicon_baba.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@mod_midwestmarbling.route("/css/<path:css>", host=_host)
def css(css):
    if "fonts" in css:
        return send_from_directory(
            os.path.join(current_app.root_path, "static/css"), css
        )
    else:
        return send_from_directory(
            os.path.join(current_app.root_path, "static/gen"), css
        )


@mod_midwestmarbling.route("/images/<folder>/<image>", host=_host)
def image_with_folder(folder, image):
    return send_from_directory(
        os.path.join(current_app.root_path, "static/images/midwestmarbling", folder),
        image,
    )


@mod_midwestmarbling.route("/images/<image>", host=_host)
def image(image):
    return send_from_directory(
        os.path.join(current_app.root_path, "static/images/midwestmarbling"), image
    )


@mod_midwestmarbling.route("/", methods=["GET"], host=_host)
def index():
    html = get_html("index.md")
    if html == "<p>404</p>":
        return abort(404)
    return render_template(
        "midwestmarbling/post.html",
        html=html["html"],
        t=_t(f"Midwest Marbling"),
    )


def get_html(page, md=None):
    top_level_list = ["index.md"]
    if page in top_level_list:
        posts_path = ""  # these pages are at the top level folder
    else:
        posts_path = "posts"
    if _host == "midwestmarbling.art":
        folder = os.path.join("templates", "midwestmarbling", posts_path)
    else:
        folder = os.path.join(os.getcwd(), "templates", "midwestmarbling", posts_path)
    git_page = os.path.join(folder, page.split("/")[-1])
    try:
        input_file = codecs.open(git_page, mode="r", encoding="utf-8")
        text = input_file.read()
        if md:
            text += md
    except:
        text = "404"

    return {
        "html": markdown.markdown(
            text,
            extensions=[
                "markdown.extensions.footnotes",
                "markdown.extensions.sane_lists",
                "markdown.extensions.toc",
                "markdown.extensions.tables",
                "markdown.extensions.def_list",
                "markdown.extensions.abbr",
                "markdown.extensions.nl2br",
                "md_in_html",
            ],
        )
    }
