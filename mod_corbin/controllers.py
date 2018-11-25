#!/usr/bin/env python
# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, redirect,\
                  url_for, flash, send_from_directory, abort
from app import app #, ix
from datetime import date, timedelta
import os
import markdown
import codecs
import requests
import json
import re
import unicodedata

mod_corbin = Blueprint('corbin', __name__)

testing = app.config['CORBIN_TEST']
if not testing:
  host = 'corbindewitt.com'
else:
  host = 'localhost:5000'

##########
# Routes #
##########

# -------
# Rather than futz with the jekyll code I already have,
# catch the static paths and send the correct static file
# /------

@mod_corbin.route('/favicon.ico', host=host)
def favicon():
  return send_from_directory(os.path.join(app.root_path, 'static'),
                             'favicon_corbin.ico', mimetype='image/vnd.microsoft.icon')

@mod_corbin.route('/css/<path:css>', host=host)
def css(css):
  if 'fonts' in css:
    return send_from_directory(os.path.join(app.root_path, 'static/css'), css)
  else:
    return send_from_directory(os.path.join(app.root_path, 'static/gen'), css)

@mod_corbin.route('/images/<folder>/<image>', host=host)
def image_with_folder(folder, image):
  return send_from_directory(os.path.join(app.root_path, 'static/images', folder), image)

@mod_corbin.route('/images/<image>', host=host)
def image(image):
  return send_from_directory(os.path.join(app.root_path, 'static/images'), image)

@mod_corbin.route('/', methods=['GET'], host=host)
def index():
  page = 'corbin/index.md'
  html = get_html(page)
  return render_template('corbin/post.html', html=html, t='corbin dewitt')

@mod_corbin.route('/downloads/<doc>', methods=['GET'], host=host)
def download(doc):
  return send_from_directory('files', doc)

@mod_corbin.route('/<title>', methods=['GET'], host=host)
def page(title):
  page = 'corbin/%s.md' % title
  html = get_html(page)
  if html == '<p>404</p>':
    return abort(404)
  return render_template('corbin/post.html', html=html, t='{0} – corbin dewitt'.format(title))

def get_html(page, dictionary_entry=False):
  filepath = os.path.join(app.root_path, 'templates', page)
  try:
    input_file = codecs.open(filepath, mode="r", encoding="utf-8")
    text = input_file.read()
  except:
    text = '404'
  return markdown.markdown(text)
