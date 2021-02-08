#!/usr/bin/env python
# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, redirect,\
                  url_for, flash, send_from_directory, abort
from app import app #, ix
from datetime import date, timedelta
from mod_parryc.models import Entry
from sqlalchemy import or_
import os
import markdown
import codecs
import requests
import json
import re
import unicodedata
# from whoosh.qparser import QueryParser
# https://urllib3.readthedocs.io/en/latest/user-guide.html#ssl-py2
# import urllib3.contrib.pyopenssl
# urllib3.contrib.pyopenssl.inject_into_urllib3()

mod_parryc = Blueprint('parryc', __name__)

testing = app.config['PARRYC_TEST']
if not testing:
  host = 'parryc.com'
else:
  host = 'localhost:5000'

##########
# Routes #
##########

# -------
# Rather than futz with the jekyll code I already have,
# catch the static paths and send the correct static file
# /------

@mod_parryc.route('/favicon.ico', host=host)
def favicon():
  return send_from_directory(os.path.join(app.root_path, 'static'),
                             'favicon.ico', mimetype='image/vnd.microsoft.icon')

@mod_parryc.route('/keybase.txt', host=host)
def keybase():
  return send_from_directory(os.path.join(app.root_path, 'static'), 'keybase.txt')

@mod_parryc.route('/css/<css>', host=host)
def css(css):
  return send_from_directory(os.path.join(app.root_path, 'static/gen'), css)

@mod_parryc.route('/images/<folder>/<image>', host=host)
def image_with_folder(folder, image):
  return send_from_directory(os.path.join(app.root_path, 'static/images', folder), image)

@mod_parryc.route('/images/<image>', host=host)
def image(image):
  return send_from_directory(os.path.join(app.root_path, 'static/images'), image)

@mod_parryc.route('/', methods=['GET'], host=host)
def index():
  page = 'parryc/index.md'
  html = get_html(page)
  return render_template('parryc/post.html',html=html)

@mod_parryc.route('/downloads/<doc>', methods=['GET'], host=host)
def download(doc):
  return send_from_directory('files', doc)

@mod_parryc.route('/<title>', methods=['GET'], host=host)
def page(title):
  page = 'parryc/%s.md' % title
  html = get_html(page)
  if html == '<p>404</p>':
    return abort(404)
  return render_template('parryc/post.html',html=html, lang='ge')

# ---------
#  Start Dict
# ---------

@mod_parryc.route('/<lang>/search', methods=['GET', 'POST'], host=host)
def dict_search_index(lang):
  dictionary_name = ''
  if lang == 'kb':
    dictionary_name = 'kabardian-english dictionary'
  print(request.form)
  if 'transliterate' not in request.form:
    transliterate = 0
  else:
    transliterate = 1
  if request.method == 'POST':
    return redirect(url_for('.dict_search'
                           ,search=request.form['search']
                           ,scope=request.form['scope']
                           ,transliterate=transliterate
                           ,lang=lang
                           ,dictionary_name=dictionary_name))
  return render_template('parryc/dictionary/search.html', lang=lang, dictionary_name=dictionary_name)

@mod_parryc.route('/<lang>/<lemma>', methods=['GET'], host=host)
def dict_lemma(lang, lemma):
  page = 'words/%s.txt' % lemma
  html = get_html(page, dictionary_entry=True)
  if html == '<p>404</p>':
    return abort(404)
  return render_template('parryc/dictionary/entry.html',html=html)

@mod_parryc.route('/<lang>/search/<search>', methods=['GET'], host=host)
def dict_search(lang, search):
  transliterate = request.args.get("transliterate")
  if transliterate == "1":
    search = _transliterate_kb(search)
  original_search = search
  search = f"%{search}%"
  scope = request.args.get("scope")

  results = []
  if scope == "headword":
    results = Entry.query.filter(
              Entry.word.ilike(search)
          ).all()
  if scope == "meaning":
    results = Entry.query.filter(
              Entry.meaning.ilike(search)
          ).all()
  if scope == "both":
    results = Entry.query.filter(
              or_(Entry.word.ilike(search),
                  Entry.meaning.ilike(search)
              )
          ).all()
  return render_template('parryc/dictionary/results.html',results=results, lang=lang, search=original_search)

@mod_parryc.route('/<lang>/browse', methods=['GET'], host=host)
def dict_browse(lang):
  browse = f"{lang}_browse.json"
  filepath = os.path.join(app.root_path, 'templates', 'parryc', 'dictionary', browse)
  with open(filepath, 'r') as file:
    indices = json.load(file)
  return render_template('parryc/dictionary/browse.html', lang=lang, indices=indices, main_page=True)

@mod_parryc.route('/<lang>/browse/<letter>', methods=['GET'], host=host)
def dict_browse_secondary(lang, letter):
  browse = f"{lang}_browse.json"
  filepath = os.path.join(app.root_path, 'templates', 'parryc', 'dictionary', browse)
  with open(filepath, 'r') as file:
    indices = json.load(file)
  if letter:
    # TODO: need to do something about digraphs/trigraphs/quadgraphs
    # and filter them out
    entries  = Entry.query.filter(Entry.word.ilike(f"{letter}%")).all()
  secondary = None
  if letter in indices['secondary']:
    secondary = indices['secondary'][letter]
  return render_template('parryc/dictionary/browse.html', lang=lang
                        , indices=indices, entries=entries
                        , letter=letter
                        , secondary=secondary)

@mod_parryc.route('/<lang>/browse/<letter>/<sec_letter>', methods=['GET'], host=host)
def dict_browse_tertiary(lang, letter, sec_letter):
  browse = f"{lang}_browse.json"
  filepath = os.path.join(app.root_path, 'templates', 'parryc', 'dictionary', browse)
  with open(filepath, 'r') as file:
    indices = json.load(file)
  if sec_letter:
    entries  = Entry.query.filter(Entry.word.ilike(f"{letter}{sec_letter}%")).all()
  return render_template('parryc/dictionary/browse.html', lang=lang
                        , indices=indices, entries=entries
                        , letter=letter
                        , secondary=indices['secondary'][letter])



# ---------
#  End Dict
# ---------

def get_html(page, dictionary_entry=False):
  filepath = os.path.join(app.root_path, 'templates', page)
  try:
    input_file = codecs.open(filepath, mode="r", encoding="utf-8")
    text = input_file.read()
  except:
    text = '404'
  if dictionary_entry:
    text = _clean_dictionary(page.split('/')[1], text)
  return markdown.markdown(text, extensions=['markdown.extensions.footnotes'
                     ,'markdown.extensions.sane_lists'
                     ,'markdown.extensions.toc'
                     ,'markdown.extensions.tables'
                     ,'markdown.extensions.def_list'
                     ,'markdown.extensions.abbr'])


def _clean_dictionary(filename, entry):
  KZ = r'([а-өА-Ө~«-][а-өА-Ө ~–?\.!,«»-]+[а-өА-Ө~?\.!,»])'
  # ай-ай-күні
  # doesn't seem to want to catch things with a lot of dashes

  # Make sure that it's composed correctly
  filename = unicodedata.normalize('NFC', filename)
  # Make sure there is always a space in front of parentheticals
  entry = re.sub(r'\(',' (',entry)
  # The regex above doesn't support single word lemmas
  filename_length = len(re.sub(r'-\d','',filename[:-4]))
  # Bold Kazakh words/phrases
  entry = re.sub(KZ,r'**\1**',entry)
  # Code mark lemma
  if filename_length <= 2:
    len_re = re.compile(u'(.{'+unicode(filename_length)+u'})')
    entry = re.sub(len_re,r'**`\1`**',entry,1) 
  else:
    entry = re.sub(KZ,r'`\1`',entry,1)
  # Make additional senses more distinct
  entry = re.sub(r'(\d+)',r'\n\1',entry)
  # Add another entry in front of the numbers so that Markdown recognizes it 
  entry = re.sub(r'(\d+)',r'\n\1',entry,1)
  # Italicize parenthenticals
  entry = re.sub(r'([\(\[].+?[\)\]])',r'_\1_',entry)
  # Differentiate sense from examples
  ## Multiple senses
  if '1.' in entry:
    entry = re.sub(r'(\n.*?)(\*\*[а-ө~])',r'\1\n\2',entry)
  else:
    entry = re.sub(r'(^.*?)(\*\*[а-ө~])',r'\1\n\2',entry)

  # replace “”
  entry = re.sub(r'“|”','"',entry)
  # remove entry ending ;
  entry = re.sub(r'; ?\n','\n',entry)
  # Remove extra spaces
  entry = re.sub(r' +',' ',entry)
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
    ("ю", "ju")
  ]
  second_pairs = [
    ("хь", "h"),
    ("ӏ", "1"),
    ("э", "e"),
    ("ь", "\""),
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
    ("а", "a")
  ]
  for cyrillic, latin in first_pairs:
    word = word.replace(latin, cyrillic)
  
  for cyrillic, latin in second_pairs:
    word = word.replace(latin, cyrillic)
  
  print(word)
  return word