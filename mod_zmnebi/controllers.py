#!/usr/bin/env python
# coding: utf-8
from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
    send_from_directory,
)
from app import app
from git import Repo
from bracket_table.bracket_table import BracketTable

# from doctor_leipzig import Leipzig
import os
import markdown
import codecs
import re

mod_zmnebi = Blueprint("zmnebi.com", __name__)

testing = app.config["ZMNEBI_TEST"]
if not testing:
    host = "zmnebi.com"
    if not (
        app.config["ZMNEBI_TEST"]
        or app.config["LEFLAN_TEST"]
        or app.config["PARRYC_TEST"]
        or app.config["CORBIN_TEST"]
        or app.config["KHACHAPURI_TEST"]
        or app.config["AVAR_TEST"]
    ):
        repo = Repo("/srv/data/vcs/git/default.git")
        folder = os.path.join("templates", "zmnebi")
else:
    host = "localhost:5000"
    repo = Repo(os.getcwd())
    folder = os.path.join(os.getcwd(), "templates", "zmnebi")


##########
# Routes #
##########


@mod_zmnebi.route("/favicon.ico", host=host)
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon_zmna.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@mod_zmnebi.route("/robots.txt", host=host)
def robots():
    return render_template("robots.txt")


@mod_zmnebi.route("/css/<path:css>", host=host)
def css(css):
    if "fonts" in css:
        return send_from_directory(os.path.join(app.root_path, "static/css"), css)
    else:
        return send_from_directory(os.path.join(app.root_path, "static/gen"), css)


@mod_zmnebi.route("/images/<folder>/<image>", host=host)
def image_with_folder(folder, image):
    return send_from_directory(
        os.path.join(app.root_path, "static/images", folder), image
    )


@mod_zmnebi.route("/images/<image>", host=host)
def image(image):
    return send_from_directory(os.path.join(app.root_path, "static/images"), image)


@mod_zmnebi.route("/", methods=["GET"], host=host)
def r():
    page = "zmnebi/verbs.md"
    html = get_html(page)
    return render_template(
        "zmnebi/post.html",
        html=html,
        title="recent updates",
        t="Georgian Verbs | ქართული ზმნები",
    )


def get_html(page):
    filepath = os.path.join(app.root_path, "templates", page)
    git_page = os.path.join(folder, page.split("/")[-1])
    input_file = codecs.open(filepath, mode="r", encoding="utf-8")
    text = input_file.read()
    time = repo.git.log("-n 1", "--format=%ci", "--", git_page)
    time = " ".join(time.split(" ")[0:2])
    text = "_Last updated {0}_\n\n".format(time) + text
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
