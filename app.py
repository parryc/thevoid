#!/usr/bin/env python
# coding: utf-8
from flask import Flask, render_template, request, send_from_directory
from flask.ext.assets import Environment, Bundle
import os

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
app.url_map.host_matching = True
assets = Environment(app)

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
  'css_lib': Bundle('css/lib/normalize.css'
               ,'css/lib/skeleton.css'
               ,'css/style.css'
               ,'css/fonts/ptsans/fonts.css'
               ,filters='cssmin',output='gen/packed.css'),
  'parryc_css': Bundle('css/marx.min.css'
               ,'css/style.css'
               ,'css/fonts/ptsans/fonts.css'
               ,filters='cssmin',output='gen/parryc.css'),

  # jQuery migrate is used to support older jQuery libraries that have been upgraded to 1.10
  'js_lib' : Bundle('js/lib/jquery-1.10.2.min.js'
               ,'js/lib/jquery-migrate-1.2.1.min.js'
               ,'js/lib/jquery-debounce-1.0.5.js'
               ,'js/lib/handlebars-runtime.js'
               ,'js/init.js'
               ,filters='jsmin',output='gen/packed.js'
          )
  }
assets.register(bundles)  


# Import a module / component using its blueprint handler variable
from mod_parryc.controllers import mod_parryc
app.register_blueprint(mod_parryc)
from mod_leflan.controllers import mod_leflan
app.register_blueprint(mod_leflan)
from mod_thebookofd.controllers import mod_thebookofd
app.register_blueprint(mod_thebookofd)
