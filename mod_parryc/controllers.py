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

from mod_parryc.models import Entry
from sqlalchemy import or_
from app import testing_site
from bracket_table.bracket_table import BracketTable
from git import Repo
import os
import markdown
import codecs
import json
import re
import unicodedata

mod_parryc = Blueprint("parryc", __name__)

if testing_site == "PARRYC":
    _host = "localhost:5000"
else:
    _host = "parryc.com"


@mod_parryc.route("/favicon.ico", host=_host)
def favicon():
    return send_from_directory(
        os.path.join(current_app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@mod_parryc.route("/css/<path:css>", host=_host)
def css(css):
    if "fonts" in css:
        return send_from_directory(
            os.path.join(current_app.root_path, "static/css"), css
        )
    else:
        return send_from_directory(
            os.path.join(current_app.root_path, "static/gen"), css
        )


@mod_parryc.route("/images/<folder>/<image>", host=_host)
def image_with_folder(folder, image):
    return send_from_directory(
        os.path.join(current_app.root_path, "static/images", folder), image
    )


@mod_parryc.route("/images/<image>", host=_host)
def image(image):
    return send_from_directory(
        os.path.join(current_app.root_path, "static/images"), image
    )


@mod_parryc.route("/", methods=["GET"], host=_host)
def index():
    page = "parryc/index.md"
    html = get_html(page)
    return render_template(
        "parryc/post.html", html=html["html"], time=html["time"], host=_host
    )


@mod_parryc.route("/downloads/<doc>", methods=["GET"], host=_host)
def download(doc):
    return send_from_directory("files", doc)


@mod_parryc.route("/archive", methods=["GET"], host=_host)
def archive():
    page = os.path.join("parryc", f"archive.md")
    html = get_html(page)
    if html == "<p>404</p>":
        return abort(404)
    return render_template("parryc/post.html", html=html["html"], time=html["time"])


@mod_parryc.route("/language/texts/<language>/<title>", host=_host)
def language_texts(language, title):
    path = "leflan"
    path = os.path.join(path, f"through-reading_{language}")
    page = os.path.join(path, f"{title}.md")
    html = get_html(page)
    if html == "<p>404</p>":
        return abort(404)
    override_titles = {"bayau": "bayau/баяу/slowly", "mooz": "mooz/мұз/ice"}
    if title not in override_titles:
        title = title.replace("_", " ")
    else:
        title = override_titles[title]
    return render_template(
        "parryc/post.html", html=html["html"], time=html["time"], override_title=title
    )


@mod_parryc.route("/language/<title>", host=_host)
def language(title):
    path = "leflan"
    page = os.path.join(path, f"language_{title}.md")
    html = get_html(page)
    if html == "<p>404</p>":
        return abort(404)
    return render_template(
        "parryc/post.html", html=html["html"], time=html["time"], override_title=title
    )


@mod_parryc.route("/books/<year>", host=_host)
def books(year):
    path = "leflan"
    page = os.path.join(path, f"books_books-{year}.md")
    html = get_html(page)
    if html == "<p>404</p>":
        return abort(404)
    return render_template(
        "parryc/post.html",
        html=html["html"],
        time=html["time"],
        override_title=f"books: {year}",
    )


@mod_parryc.route("/<path:title>", methods=["GET"], host=_host)
@mod_parryc.route("/archive/<path:title>", methods=["GET"], host=_host)
def page(title):
    path = "parryc"
    if "/" in title:
        path = os.path.join(path, "archive")
    page = os.path.join(path, f"{title}.md")
    html = get_html(page)
    if html["html"] == "<p>404</p>":
        return abort(404)
    return render_template("parryc/post.html", html=html["html"], time=html["time"])


# ---------
#  Start Dict
# ---------


@mod_parryc.route("/<lang>/search", methods=["GET", "POST"], host=_host)
def dict_search_index(lang):
    dictionary_name = ""
    if lang == "kb":
        dictionary_name = "kabardian-english dictionary"

    if "transliterate" not in request.form:
        transliterate = 0
    else:
        transliterate = 1
    if request.method == "POST":
        return redirect(
            url_for(
                ".dict_search",
                searcsite=request.form["search"],
                scope=request.form["scope"],
                transliterate=transliterate,
                lang=lang,
                dictionary_name=dictionary_name,
            )
        )
    return render_template(
        "parryc/dictionary/search.html", lang=lang, dictionary_name=dictionary_name
    )


@mod_parryc.route("/<lang>/<lemma>", methods=["GET"], host=_host)
def dict_lemma(lang, lemma):
    page = "words/%s.txt" % lemma
    html = get_html(page, dictionary_entry=True)
    if html == "<p>404</p>":
        return abort(404)
    return render_template("parryc/dictionary/entry.html", html=html)


@mod_parryc.route("/<lang>/search/<search>", methods=["GET"], host=_host)
def dict_search(lang, search):
    transliterate = request.args.get("transliterate")
    if transliterate == "1":
        search = _transliterate_kb(search)
    original_search = search
    search = f"%{search}%"
    scope = request.args.get("scope")

    results = []
    if scope == "headword":
        results = Entry.query.filter(Entry.word.ilike(search)).all()
    if scope == "meaning":
        results = Entry.query.filter(Entry.meaning.ilike(search)).all()
    if scope == "both":
        results = Entry.query.filter(
            or_(Entry.word.ilike(search), Entry.meaning.ilike(search))
        ).all()
    return render_template(
        "parryc/dictionary/results.html",
        results=results,
        lang=lang,
        searcsite=original_search,
    )


@mod_parryc.route("/<lang>/browse", methods=["GET"], host=_host)
def dict_browse(lang):
    browse = f"{lang}_browse.json"
    filepath = os.path.join(
        current_app.root_path, "templates", "parryc", "dictionary", browse
    )
    with open(filepath, "r") as file:
        indices = json.load(file)
    return render_template(
        "parryc/dictionary/browse.html", lang=lang, indices=indices, main_page=True
    )


@mod_parryc.route("/<lang>/browse/<letter>", methods=["GET"], host=_host)
def dict_browse_secondary(lang, letter):
    browse = f"{lang}_browse.json"
    filepath = os.path.join(
        current_app.root_path, "templates", "parryc", "dictionary", browse
    )
    with open(filepath, "r") as file:
        indices = json.load(file)
    if letter:
        # TODO: need to do something about digraphs/trigraphs/quadgraphs
        # and filter them out
        entries = Entry.query.filter(Entry.word.ilike(f"{letter}%")).all()
    secondary = None
    if letter in indices["secondary"]:
        secondary = indices["secondary"][letter]
    return render_template(
        "parryc/dictionary/browse.html",
        lang=lang,
        indices=indices,
        entries=entries,
        letter=letter,
        secondary=secondary,
    )


@mod_parryc.route("/<lang>/browse/<letter>/<sec_letter>", methods=["GET"], host=_host)
def dict_browse_tertiary(lang, letter, sec_letter):
    browse = f"{lang}_browse.json"
    filepath = os.path.join(
        current_app.root_path, "templates", "parryc", "dictionary", browse
    )
    with open(filepath, "r") as file:
        indices = json.load(file)
    if sec_letter:
        entries = Entry.query.filter(Entry.word.ilike(f"{letter}{sec_letter}%")).all()
    return render_template(
        "parryc/dictionary/browse.html",
        lang=lang,
        indices=indices,
        entries=entries,
        letter=letter,
        secondary=indices["secondary"][letter],
    )


# ---------
#  End Dict
# ---------


def get_html(page, dictionary_entry=False):
    if _host == "parryc.com":
        repo = Repo("/srv/data/vcs/git/default.git")
        folder_leflan = os.path.join("templates", "leflan")
        folder_parryc = os.path.join("templates", "parryc")
    else:
        repo = Repo(os.getcwd())
        folder_leflan = os.path.join(os.getcwd(), "templates", "leflan")
        folder_parryc = os.path.join(os.getcwd(), "templates", "parryc")
    git_page = os.path.join(folder_leflan, page.split("/")[-1])
    if page == "parryc/index.md":
        time = ""  # no last updated for index
    elif "through-reading" in page or "through-writing" in page:
        path_parts = page.split("/")
        if "index.md" in page:
            # go up to the folder level to get the most recent subpage's change
            # page_parts = page.split('/')
            git_page = os.path.join(folder_leflan, path_parts[-2])
            time = repo.git.log("-n 1", "--format=%ci", "--", git_page)
        else:
            git_page = os.path.join(folder_leflan, path_parts[-2], path_parts[-1])
            time = repo.git.log("-n 1", "--format=%ci", "--", git_page)
    else:
        time = repo.git.log("-n 1", "--format=%ci", "--", git_page)
        if not time:
            git_page = os.path.join(folder_parryc, page.split("/")[-1])
            time = repo.git.log("-n 1", "--format=%ci", "--", git_page)
    time = " ".join(time.split(" ")[0:2])
    filepath = os.path.join(current_app.root_path, "templates", page)
    try:
        input_file = codecs.open(filepath, mode="r", encoding="utf-8")
        text = input_file.read()
    except:
        text = "404"
    if dictionary_entry:
        text = _clean_dictionary(page.split("/")[1], text)

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
                "mod_leflan.furigana",
                BracketTable(),
                "doctor_leipzig.doctor_leipzig",
                "mod_leflan.examples",
                "md_in_html",
            ],
        ),
        "time": time,
    }


def _clean_dictionary(filename, entry):
    KZ = r"([а-өА-Ө~«-][а-өА-Ө ~–?\.!,«»-]+[а-өА-Ө~?\.!,»])"
    # ай-ай-күні
    # doesn't seem to want to catch things with a lot of dashes

    # Make sure that it's composed correctly
    filename = unicodedata.normalize("NFC", filename)
    # Make sure there is always a space in front of parentheticals
    entry = re.sub(r"\(", " (", entry)
    # The regex above doesn't support single word lemmas
    filename_length = len(re.sub(r"-\d", "", filename[:-4]))
    # Bold Kazakh words/phrases
    entry = re.sub(KZ, r"**\1**", entry)
    # Code mark lemma
    if filename_length <= 2:
        len_re = re.compile("(.{" + unicode(filename_length) + "})")
        entry = re.sub(len_re, r"**`\1`**", entry, 1)
    else:
        entry = re.sub(KZ, r"`\1`", entry, 1)
    # Make additional senses more distinct
    entry = re.sub(r"(\d+)", r"\n\1", entry)
    # Add another entry in front of the numbers so that Markdown recognizes it
    entry = re.sub(r"(\d+)", r"\n\1", entry, 1)
    # Italicize parenthenticals
    entry = re.sub(r"([\(\[].+?[\)\]])", r"_\1_", entry)
    # Differentiate sense from examples
    ## Multiple senses
    if "1." in entry:
        entry = re.sub(r"(\n.*?)(\*\*[а-ө~])", r"\1\n\2", entry)
    else:
        entry = re.sub(r"(^.*?)(\*\*[а-ө~])", r"\1\n\2", entry)

    # replace “”
    entry = re.sub(r"“|”", '"', entry)
    # remove entry ending ;
    entry = re.sub(r"; ?\n", "\n", entry)
    # Remove extra spaces
    entry = re.sub(r" +", " ", entry)
    return entry


def _transliterate_kb(word):
    first_pairs = [
        ("жь", "zhh"),
        ("щ", "shh"),
        ("ш", "sh"),
        ("ч", "ch"),
        ("ж", "zh"),
        ("й", "jj"),
        ("и", "ji"),
        ("е", "je"),
        ("я", "ja"),
        ("ю", "ju"),
    ]
    second_pairs = [
        ("хь", "h"),
        ("ӏ", "1"),
        ("э", "e"),
        ("ь", '"'),
        ("ы", "i"),
        ("ъ", "'"),
        ("ц", "c"),
        ("х", "x"),
        ("ф", "f"),
        ("у", "w"),
        ("т", "t"),
        ("с", "s"),
        ("р", "r"),
        ("п", "p"),
        ("о", "o"),
        ("н", "n"),
        ("м", "m"),
        ("л", "l"),
        ("к", "k"),
        ("з", "z"),
        ("д", "d"),
        ("г", "g"),
        ("в", "v"),
        ("б", "b"),
        ("а", "a"),
    ]
    for cyrillic, latin in first_pairs:
        word = word.replace(latin, cyrillic)

    for cyrillic, latin in second_pairs:
        word = word.replace(latin, cyrillic)

    return word
