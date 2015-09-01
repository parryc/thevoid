#!/usr/bin/env python
# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, redirect,\
                  url_for, flash, send_from_directory
from app import app
import os
import markdown
import codecs

mod_parryc = Blueprint('parryc', __name__)

prod = False
if prod:
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
  return render_template('parryc/index.html')

@mod_parryc.route('/categories/<category>', methods=['GET'], host=host)
@mod_parryc.route('/categories/<category>/', methods=['GET'], host=host)
def category(category):
  page = 'parryc/categories/%s/index.html' % category
  return render_template(page)

@mod_parryc.route('/<title>', methods=['GET'], host=host)
def page(title):
  page = 'parryc/%s.md' % title
  filepath = os.path.join(app.root_path, 'templates', page)
  input_file = codecs.open(filepath, mode="r", encoding="utf-8")
  text = input_file.read()
  html = markdown.markdown(text)
  return render_template('parryc/post.html',html=html)

