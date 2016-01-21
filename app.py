#!/usr/bin/env python
# coding: utf-8
from flask import Flask, render_template, request, send_from_directory
from flask.ext.assets import Environment, Bundle
import os

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
app.url_map.host_matching = True
assets = Environment(app)

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
               ,filters='cssmin',output='gen/leflan.css')
  }
assets.register(bundles)  


# Import a module / component using its blueprint handler variable
from mod_parryc.controllers import mod_parryc
app.register_blueprint(mod_parryc)
from mod_leflan.controllers import mod_leflan
app.register_blueprint(mod_leflan)
from mod_thebookofd.controllers import mod_thebookofd
app.register_blueprint(mod_thebookofd)
