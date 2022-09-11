from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
    abort,
    current_app,
)

from app import testing_site
from git import Repo
import os
import markdown
import codecs

mod_bookarts = Blueprint("bookarts", __name__)

if testing_site == "BOOKARTS":
    _host = "localhost:5000"
else:
    _host = "bookartbook.art"


def _t(title):
    return f"{title}"


@mod_bookarts.route("/favicon.ico", host=_host)
def favicon():
    return send_from_directory(
        os.path.join(current_app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@mod_bookarts.route("/css/<path:css>", host=_host)
def css(css):
    if "fonts" in css:
        return send_from_directory(
            os.path.join(current_app.root_path, "static/css"), css
        )
    else:
        return send_from_directory(
            os.path.join(current_app.root_path, "static/gen"), css
        )


@mod_bookarts.route("/images/<folder>/<image>", host=_host)
def image_with_folder(folder, image):
    return send_from_directory(
        os.path.join(current_app.root_path, "static/images", folder), image
    )


@mod_bookarts.route("/images/<image>", host=_host)
def image(image):
    return send_from_directory(
        os.path.join(current_app.root_path, "static/images"), image
    )


@mod_bookarts.route("/", methods=["GET"], host=_host)
def index():
    html = get_html("index.md")
    if html == "<p>404</p>":
        return abort(404)
    return render_template(
        "bookarts/post.html",
        html=html["html"],
        time=html["time"],
        t=_t(f"bookartbook.art"),
    )


@mod_bookarts.route("/<title>", methods=["GET"], host=_host)
def post(title):
    html = get_html(f"{title}.md")
    if html == "<p>404</p>":
        return abort(404)
    return render_template(
        "bookarts/post.html",
        html=html["html"],
        time=html["time"],
        override_title=title.replace("-", " "),
        t=_t(f"bookartbook.art"),
    )


def get_html(page):
    if _host == "bookartbook.art":
        repo = Repo("/srv/data/vcs/git/default.git")
        folder = os.path.join("templates", "bookarts")
    else:
        repo = Repo(os.getcwd())
        folder = os.path.join(os.getcwd(), "templates", "bookarts")
    git_page = os.path.join(folder, page.split("/")[-1])
    if page == "index.md":
        time = ""  # no last updated for index
    else:
        time = repo.git.log("-n 1", "--format=%ci", "--", git_page)
        if not time:
            git_page = os.path.join(folder, page.split("/")[-1])
            time = repo.git.log("-n 1", "--format=%ci", "--", git_page)
    time = " ".join(time.split(" ")[0:2])
    try:
        input_file = codecs.open(git_page, mode="r", encoding="utf-8")
        text = input_file.read()
        if page == "bookarts/index.md":
            text += _recent()
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
        ),
        "time": time,
    }


def _recent():
    text = ""
    if _host == "bookartbook.art":
        repo = Repo("/srv/data/vcs/git/default.git")
        folder = os.path.join("templates", "bookarts")
    else:
        repo = Repo(os.getcwd())
        folder = os.path.join(os.getcwd(), "templates", "parryc")
    for filename in sorted(
        os.listdir(folder),
        key=lambda _file: repo.git.log(
            "-n 1", "--format=%ci", "--", os.path.join(folder, _file)
        ),
        reverse=True,
    ):
        _parts = filename.split("_")
        if _parts[0] != ".DS":
            page_name = _parts[1].replace(".md", "").replace("-", " ")
            url = "/".join(["posts", page_name])
            text += f"* [{url}]({page_name})"
    return text
