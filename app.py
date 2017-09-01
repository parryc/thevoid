#!/usr/bin/env python
# coding: utf-8
from flask import Flask, render_template, request, send_from_directory
from flask.ext.assets import Environment, Bundle
from flask_sqlalchemy import SQLAlchemy
import os
import codecs
import re
from whoosh.index import create_in
from whoosh.fields import *

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
app.url_map.host_matching = True
assets = Environment(app)
db = SQLAlchemy(app)

def circle_num_from_jinja_loop(num):
  return u'①②③④⑤⑥⑦⑧⑨⑩'[num-1]

app.jinja_env.filters['circle_num'] = circle_num_from_jinja_loop

# clear the automatically added route for static
# https://github.com/mitsuhiko/flask/issues/1559
# enable host matching and re-add the static route with the desired host
app.add_url_rule(app.static_url_path + '/<path:filename>',
                 endpoint='static',
                 view_func=app.send_static_file)

@app.errorhandler(404)
def not_found(error):
  # print request.host
  return render_template('404.html'), 404

# Define static asset bundles to be minimized and deployed
bundles = {
  'parryc_css': Bundle('css/marx.min.css'
               ,'css/style_parryc.css'
               ,'css/fonts/ptsans/fonts.css'
               ,filters='cssmin',output='gen/parryc.css'),
  'leflan_css': Bundle('css/marx.min.css'
               ,'css/style_leflan.css'
               ,'css/fonts/source-code-pro/source-code-pro.css'
               ,'css/fonts/cmu/fonts.css'
               ,filters='cssmin',output='gen/leflan.css')
  }
assets.register(bundles)  

######################
# SETUP WHOOSH INDEX #
######################

# content is not stored in the index, thought it is indexed, because
# we have the raw files
schema = Schema(title=TEXT(stored=True),
                path=ID(stored=True),
                summary=TEXT(stored=True),
                etym=TEXT(stored=True),
                tag=TEXT(stored=True),
                content=TEXT)
ix = create_in('indexdir', schema)
writer = ix.writer()
for filename in sorted(os.listdir('templates/words'))[1:10]:
  filename = filename.decode('UTF-8')
  path = u'templates/words/{}'.format(filename)
  with codecs.open(path,'r','utf-8') as in_file:
    content = in_file.read()
    etym = re.search(ur'(\[.*?\])',content)
    if etym:
      etym = etym.group(0)[1:-1]
    else:
      etym = u""

    tag = re.search(ur'(\(.*?\))',content)
    if tag:
      tag = tag.group(0)[1:-1]
    else:
      tag = u""

    writer.add_document(title=filename[:-4],
                        path=path,
                        summary=' '.join(content.split(' ')[0:20]) + '...',
                        etym=etym,
                        tag=tag,
                        content=content)
writer.commit()

# Import a module / component using its blueprint handler variable
from mod_parryc.controllers import mod_parryc
app.register_blueprint(mod_parryc)
from mod_leflan.controllers import mod_leflan
app.register_blueprint(mod_leflan)
