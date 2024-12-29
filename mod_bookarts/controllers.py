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
        "favicon_baba.ico",
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
        os.path.join(current_app.root_path, "static/images/bookarts", folder), image
    )


@mod_bookarts.route("/images/<folder>/<folder2>/<image>", host=_host)
def image_with_two_folders(folder, folder2, image):
    return send_from_directory(
        os.path.join(current_app.root_path, "static/images/bookarts", folder, folder2), image
    )


@mod_bookarts.route("/images/<image>", host=_host)
def image(image):
    return send_from_directory(
        os.path.join(current_app.root_path, "static/images/bookarts"), image
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


@mod_bookarts.route("/posts", methods=["GET"], host=_host)
def posts():
    def _clean_filename(name):
        return name.replace("-", " ")

    def _category_description(cat):
        desc = ""
        if cat == "bookbinding":
            desc = "creating that delicious sandwich of two covers and a bookblock"
        if cat == "experiments":
            desc = (
                "research into various aspects of the craft. "
                "may be tedious or might answer questions you have as well."
            )
        if cat == "lecture notes":
            desc = (
                "notes from lectures either attended in person or watched on line. "
                "may not actually be a lecture, per se."
            )
        if cat == "materials":
            desc = "dealing with the star stuff of book arts."
        if cat == "marbling":
            desc = "all things marbling, mostly acrylic, often about rakes."
        if cat == "paper":
            desc = "on my ever growing infatuation with all the varieties of the world."
        if cat == "projects":
            desc = "standalone projects with a concrete end result."
        if cat == "letterpress":
            desc = "all the posts that are fit to print."
        if cat == "photo reel":
            desc = "pictures of the various books and arts of the bookarts."
        return "> " + desc + "\n"

    if _host == "bookartbook.art":
        folder = os.path.join("templates", "bookarts", "posts")
    else:
        folder = os.path.join(os.getcwd(), "templates", "bookarts", "posts")
    categories = {}
    for file in os.scandir(folder):
        with codecs.open(file.path, mode="r", encoding="utf-8") as f:
            file_tags = f.readlines()[0].strip().split(";")

        for tag in file_tags:
            tag_parts = tag.split(">")
            header = tag_parts[0].strip()
            filename = file.name.replace(".md", "")
            if len(tag_parts) > 1:
                subheader = tag_parts[1].strip()
            else:
                subheader = "default"
            if header not in categories:
                categories[header] = {
                    "heading": header,
                    "subheadings": {subheader: [filename]},
                }
            else:
                if subheader not in categories[header]["subheadings"]:
                    categories[header]["subheadings"][subheader] = [filename]
                else:
                    categories[header]["subheadings"][subheader].append(filename)

    _md = ""
    first = True
    for category in sorted(categories.keys()):
        if not first:
            _md += "\n----\n"
        if first:
            first = False
        _md += f"\n# {categories[category]['heading']}"
        _md += f"\n{_category_description(categories[category]['heading'])}"
        if "default" in categories[category]["subheadings"]:
            _md += "\n"
            for post in categories[category]["subheadings"]["default"]:
                _md += f"* [{_clean_filename(post)}]({post.replace('?', '%3F')})\n"
            _md += "\n"
        for subheading in categories[category]["subheadings"].keys():
            if subheading == "default":
                continue
            else:
                _md += f"\n## {subheading}\n"
            for post in categories[category]["subheadings"][subheading]:
                _md += f"* [{_clean_filename(post)}]({post.replace('?', '%3F')})\n"
    html = get_html("categories.md", md=_md)
    if _md == "<p>404</p>":
        return abort(404)
    return render_template(
        "bookarts/post.html",
        html=html["html"],
        time="",
        t=_t(f"bookartbook.art"),
        has_toc=True,
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
        has_toc="toc" in html["html"],
        t=_t(f"bookartbook.art"),
    )


def get_html(page, md=None):
    top_level_list = ["index.md", "shop.md", "categories.md"]
    if page in top_level_list:
        posts_path = ""  # these pages are at the top level folder
    else:
        posts_path = "posts"
    if _host == "bookartbook.art":
        repo = Repo("/srv/data/vcs/git/default.git")
        folder = os.path.join("templates", "bookarts", posts_path)
    else:
        repo = Repo(os.getcwd())
        folder = os.path.join(os.getcwd(), "templates", "bookarts", posts_path)
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
        if page in top_level_list:
            text = input_file.read()
        else:
            text = "".join(
                input_file.readlines()[1:]
            )  # skip first line, where metadata lies
        if page == "index.md":
            text += _recent()
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
        ),
        "time": time,
    }


def _recent():
    text = ""
    if _host == "bookartbook.art":
        repo = Repo("/srv/data/vcs/git/default.git")
        folder = os.path.join("templates", "bookarts", "posts")
    else:
        repo = Repo(os.getcwd())
        folder = os.path.join(os.getcwd(), "templates", "bookarts", "posts")
    for filename in sorted(
        os.listdir(folder),
        key=lambda _file: repo.git.log(
            "-n 1", "--format=%ci", "--", os.path.join(folder, _file)
        ),
        reverse=True,
    ):
        _parts = filename.split(".")
        if _parts[-1] == "md" and _parts[0] != "index":
            page_name = _parts[0].replace("-", " ")
            url = f"/{page_name}"
            text += f"\n* [{page_name}]({_parts[0].replace('?', '%3F')})"
    return text
