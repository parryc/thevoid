#!/usr/bin/env python
# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, redirect,\
                  url_for, flash, send_from_directory, abort
from app import app
from datetime import date, timedelta
import os
import markdown
import codecs
import requests
import json
import re
import unicodedata

mod_khachapuri = Blueprint('khachapuri', __name__)

testing = app.config['KHACHAPURI_TEST']
if not testing:
  host = 'the-yelp-of-khachapuri.site'
else:
  host = 'localhost:5000'

##########
# Routes #
##########

@mod_khachapuri.route('/favicon.ico', host=host)
def favicon():
  return send_from_directory(os.path.join(app.root_path, 'static'),
                             'favicon_khachapuri.ico', mimetype='image/vnd.microsoft.icon')

@mod_khachapuri.route('/css/<path:css>', host=host)
def css(css):
  if 'fonts' in css:
    return send_from_directory(os.path.join(app.root_path, 'static/css'), css)
  else:
    return send_from_directory(os.path.join(app.root_path, 'static/gen'), css)

@mod_khachapuri.route('/images/<folder>/<image>', host=host)
def image_with_folder(folder, image):
  return send_from_directory(os.path.join(app.root_path, 'static/images', folder), image)

@mod_khachapuri.route('/images/<image>', host=host)
def image(image):
  return send_from_directory(os.path.join(app.root_path, 'static/images'), image)

@mod_khachapuri.route('/', methods=['GET'], host=host)
def index():
  page = 'khachapuri/index.md'
  html = get_html(page)
  return render_template('khachapuri/post.html', html=html, t='the yelp of khachapuri')

@mod_khachapuri.route('/downloads/<doc>', methods=['GET'], host=host)
def download(doc):
  return send_from_directory('files', doc)

@mod_khachapuri.route('/<title>', methods=['GET'], host=host)
def page(title):
  page = 'khachapuri/%s.md' % title
  html = get_html(page)
  if html == '<p>404</p>':
    return abort(404)
  return render_template('khachapuri/post.html', html=html, t='{0} – the yelp of khachapuri'.format(title))

def get_html(page):
  filepath = os.path.join(app.root_path, 'templates', page)
  try:
    input_file = codecs.open(filepath, mode="r", encoding="utf-8")
    text = input_file.read()
  except:
    text = '404'
  return markdown.markdown(text,
          extensions=['markdown.extensions.nl2br'
                     ,'markdown.extensions.toc'
                     ,'markdown.extensions.tables'
                     ,'markdown.extensions.def_list'
                     ,'markdown.extensions.abbr'
                     ,'markdown.extensions.footnotes'
                     ])
