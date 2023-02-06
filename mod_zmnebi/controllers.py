from datetime import datetime, timezone, timedelta

from flask import (
    Blueprint,
    render_template,
    send_from_directory,
    current_app,
    make_response,
)
from git import Repo
from bracket_table.bracket_table import BracketTable
from app import testing_site
from feedgen.feed import FeedGenerator
from rss_posts import updates as rss_updates
import os
import markdown
import codecs

mod_zmnebi = Blueprint("zmnebicom", __name__)


if testing_site == "ZMNEBI":
    _host = "localhost:5000"
else:
    _host = "zmnebi.com"


@mod_zmnebi.route("/favicon.ico", host=_host)
def favicon():
    return send_from_directory(
        os.path.join(current_app.root_path, "static"),
        "favicon_zmna.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@mod_zmnebi.route("/robots.txt", host=_host)
def robots():
    return render_template("robots.txt")


@mod_zmnebi.route("/css/<path:css>", host=_host)
def css(css):
    if "fonts" in css:
        return send_from_directory(
            os.path.join(current_app.root_path, "static/css"), css
        )
    else:
        return send_from_directory(
            os.path.join(current_app.root_path, "static/gen"), css
        )


@mod_zmnebi.route("/images/<folder>/<image>", host=_host)
def image_with_folder(folder, image):
    return send_from_directory(
        os.path.join(current_app.root_path, "static/images", folder), image
    )


@mod_zmnebi.route("/images/<image>", host=_host)
def image(image):
    return send_from_directory(
        os.path.join(current_app.root_path, "static/images"), image
    )


@mod_zmnebi.route("/", methods=["GET"], host=_host)
def index():
    page = "zmnebi/verbs.md"
    html = get_html(page, _host)
    return render_template(
        "zmnebi/post.html",
        html=html,
        title="recent updates",
        t="Georgian Verbs | ქართული ზმნები",
    )


@mod_zmnebi.route("/rss", methods=["GET"], host=_host)
def rss():
    _url = "https://zmnebi.com"
    _author = "Parry"
    _email = "parry@parryc.com"
    fg = FeedGenerator()
    fg.title("Georgian Verbs | zmnebi.com")
    fg.description("All about Georgian verbs and how to use them")
    fg.link(href=_url)

    for update in rss_updates:
        fe = fg.add_entry()
        fe.title(update["title"])
        fe.link(href=update["link"])
        fe.description(update["description"])
        fe.guid(update["link"], permalink=True)
        fe.author(name=_author, email=_email)
        fe.pubDate(update["date"])

    response = make_response(fg.rss_str())
    response.headers.set("Content-Type", "application/rss+xml")

    return response


def get_html(page, host):
    if host == "zmnebi.com":
        repo = Repo("/srv/data/vcs/git/default.git")
        folder = os.path.join("templates", "zmnebi")
    else:
        repo = Repo(os.getcwd())
        folder = os.path.join(os.getcwd(), "templates", "zmnebi")
    filepath = os.path.join(current_app.root_path, "templates", page)
    git_page = os.path.join(folder, page.split("/")[-1])
    input_file = codecs.open(filepath, mode="r", encoding="utf-8")
    text = input_file.read()
    time = repo.git.log("-n 1", "--format=%ci", "--", git_page)
    time = " ".join(time.split(" ")[0:2])
    text = (
        "_Last updated {0}_\n".format(time) + "<a href='/rss'>RSS feed</a>\n\n" + text
    )
    return markdown.markdown(
        text,
        extensions=[
            "markdown.extensions.nl2br",
            "markdown.extensions.toc",
            "markdown.extensions.tables",
            "markdown.extensions.def_list",
            "markdown.extensions.abbr",
            "markdown.extensions.footnotes",
            "mod_leflan.furigana",
            BracketTable(),
            "doctor_leipzig.doctor_leipzig",
            "mod_leflan.examples",
        ],
    )
