from flask import Flask, render_template, request
from flask.ext.assets import Environment, Bundle
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.marshmallow import Marshmallow
from flask_wtf.csrf import CsrfProtect

import flask.ext.whooshalchemy as whooshalchemy
import os

app = Flask(__name__)
app.config = {}
app.config.from_object('config.DevelopmentConfig')
_dir = os.path.dirname(__file__)
app.config['WHOOSH_BASE'] = os.path.join(_dir, 'search.db')
db = SQLAlchemy(app)
assets = Environment(app)
ma = Marshmallow(app)
# csrf = CsrfProtect()
#add csrf protection across the board
# csrf.init_app(app)


@app.route('/')
def index():
  return render_template('index.html')

@app.errorhandler(404)
def not_found(error):
  return render_template('404.html'), 404

# Define static asset bundles to be minimized and deployed
bundles = {
#   'css' : Bundle('css/lib/fonts/css/font-awesome.css'
#                 ,'css/lib/bootstrap.css'
#                 ,'css/lib/bootstrap-reset.css'
#                 ,'css/lib/jquery-ui-1.10.3.css'
#                 ,'css/lib/custom-ico-fonts.css'
#                 ,'css/lib/clndr.css'
#                 ,'css/lib/style.css'
#                 ,'css/lib/style-responsive.css'
#                 ,'css/allsetlearning.css'
#                 ,filters='cssmin',output='gen/packed.css'
#           ),
#   'css_datatable' : Bundle('js/lib/data-tables/DT_bootstrap.css'
#                ,filters='cssmin',output='gen/packed_datatable.css'),
#   'css_multiselect' : Bundle('js/lib/jquery-multi-select/css/multi-select.css'
#                ,filters='cssmin',output='gen/packed_multiselect.css'),
  
  # jQuery migrate is used to support older jQuery libraries that have been upgraded to 1.10
  'js_lib' : Bundle('js/lib/jquery-1.10.2.min.js'
               ,'js/lib/jquery-migrate-1.2.1.min.js'
               ,'js/lib/jquery-debouce-1.0.5.js'
               ,filters='jsmin',output='gen/packed.js'
          ),
  'mod_beers' : Bundle('js/search.js'
               ,filters='jsmin',output='gen/search.js')
#   'js_datatable' : Bundle('js/lib/advanced-datatable/js/jquery.dataTables.js'
#                ,'js/lib/data-tables/DT_bootstrap.js'
#                ,'js/lib/dynamic_table_init.js'
#                ,filters='jsmin',output='gen/packed_datatable.js'),
#   'js_multiselect' : Bundle('js/lib/jquery-multi-select/js/jquery.multi-select.js'
#                ,'js/lib/jquery-multi-select/js/jquery.quicksearch.js'
#                ,'js/lib/multi-select-init.js'
#                ,filters='jsmin',output='gen/packed_multiselect.js'),
#   'mod_texts' : Bundle('js/mod_texts.add.js'
#                ,'js/mod_texts.add.templates.js'
#                ,'js/filter_control.js'
#                ,filters='jsmin',output='gen/mod_texts.js'),
#   'mod_sources' : Bundle('js/filter_control.js'
#                ,filters='jsmin',output='gen/mod_sources.js'),
#   'mod_sets' : Bundle('js/filter_control.js'
#                ,filters='jsmin',output='gen/mod_sets.js'),
#   'mod_dictionary' : Bundle('js/mod_dictionary.add.js'
#                ,filters='jsmin',output='gen/mod_dictionary.js'),
#   'mod_analysis' : Bundle('js/mod_analysis.run.js'
#                ,'js/mod_analysis.run.templates.js'
#                ,filters='jsmin',output='gen/mod_analysis.js')
  }
assets.register(bundles)  


# Import a module / component using its blueprint handler variable
from app.mod_beers.controllers import mod_beers
app.register_blueprint(mod_beers)
from app.mod_users.controllers import mod_users
app.register_blueprint(mod_users)
