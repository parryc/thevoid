#!/usr/bin/env python
# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, redirect,\
                  url_for, flash, send_from_directory
from app import app
from datetime import date
import os
import markdown
import codecs
import requests
import json
from mod_parryc.models import *
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
@mod_parryc.route('/css/<css>', host=host)
def css(css):
  return send_from_directory(os.path.join(app.root_path, 'static/gen'), css)

@mod_parryc.route('/images/<folder>/<image>', host=host)
def image_with_folder(folder, image):
  return send_from_directory(os.path.join(app.root_path, 'static/images', folder), image)

@mod_parryc.route('/images/<image>', host=host)
def image(image):
  return send_from_directory(os.path.join(app.root_path, 'static/images'), image)

# ------
# PaaS
# /-----

@mod_parryc.route('/paas', methods=['GET'], host=host)
def paas_index():
  return render_template('parryc/paas.html')

@mod_parryc.route('/paas/send-to-timeseries', methods=['GET','POST'], host=host)
def paas_to_timeseries():
  test = [date(2017, 6, 1), date(2017, 6, 2), date(2017, 6, 5), date(2017, 6, 8)]
  def _fill(timeblock):
    padded = []
    for idx, t in enumerate(timeblock):
      if idx + 1 == len(timeblock):
        padded.append(1)
      else:
        _next = timeblock[idx + 1]
        delta = _next - t
        if delta.days == 1:
          padded.append(1)
        else:
          padded.append(1)
          padded.extend([0] * (delta.days - 1))
    return padded

  _ts_response = {}
  if request.method == 'POST':
    # 0 = small
    # 1 = medium
    # 2 = large
    #
    save_result = add_request(request.json['request_id'], request.json['request_project_size'],
                              False, [], request.json['timeseries_interval_count'])
    print(save_result)
    if save_result['status']:
      # get the data
      _ts_response = _paas_timeseries_request("0,0,0,1,1,0,0,0,1,1,0,0,0,1,1", request.json['timeseries_interval_count'])
      print('--- ts ---')
      print(_ts_response)
      print('/---------')
  return _ts_response

@mod_parryc.route('/paas/retrieve/<int:request_id>', methods=['GET'], host=host)
def paas_lookup(request_id):
  def _get(request_id):
    # do something
    return {'response':[1,3,5,2,1,0,0,1,4,8,8,1]}
  return jsonify(_get(request_id))

# ----------
# END PAAS
# /---------

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
  return render_template('parryc/post.html',html=html)

def get_html(page):
  filepath = os.path.join(app.root_path, 'templates', page)
  input_file = codecs.open(filepath, mode="r", encoding="utf-8")
  text = input_file.read()
  return markdown.markdown(text)

def _paas_timeseries_request(inline_data, interval_count):
  endpoint = "https://i-03814497e692f802b.workdaysuv.com/advancedAnalytics/forecasting/fixedPeriod"
  params   = '{\"forecast_size\":%s}' % interval_count
  request_json = {
    "model_spec":{
      "category":"timeseries_arima",
      "params":params,
      "id":"DNU",
      "name":"DNU"
    },
    "data_frame":{
      "inline_data": inline_data
    }
  }
  ts_response = requests.post(endpoint, json=request_json)
  print('----json---')
  print(json.dumps(request_json))
  print('----/json---')
  print(ts_response.text)
  return ts_response.text

