#!/usr/bin/env python
# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, redirect,\
                  url_for, flash, send_from_directory
from app import csrf, app
from flask_wtf.csrf import CsrfProtect
import os

mod_parryc = Blueprint('parryc', __name__)

localhost = 'localhost:5000'
prod = 'parryc.com'

##########
# Routes #
##########

# -------
# Rather than futz with the jekyll code I already have,
# catch the static paths and send the correct static file
# /------

@mod_parryc.route('/favicon.ico', host=prod)
def favicon():
  return send_from_directory(os.path.join(app.root_path, 'static'),
                             'favicon.ico', mimetype='image/vnd.microsoft.icon')
@mod_parryc.route('/css/<css>', host=prod)
def css(css):
  return send_from_directory(os.path.join(app.root_path, 'static/gen'), css)

@mod_parryc.route('/images/<image>', host=prod)
def images(image):
  return send_from_directory(os.path.join(app.root_path, 'static/images'), image)


@mod_parryc.route('/', methods=['GET'], host=prod)
def index():
  return render_template('parryc/index.html')

@mod_parryc.route('/categories/<category>', methods=['GET'], host=prod)
@mod_parryc.route('/categories/<category>/', methods=['GET'], host=prod)
def category(category):
  page = 'parryc/categories/%s/index.html' % category
  return render_template(page)

@mod_parryc.route('/<title>', methods=['GET'], host=prod)
def page(title):
  page = 'parryc/%s/index.html' % title
  return render_template(page)

