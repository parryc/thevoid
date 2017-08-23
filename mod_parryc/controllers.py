#!/usr/bin/env python
# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, redirect,\
                  url_for, flash, send_from_directory, abort
from app import app, db
from datetime import date, timedelta
import os
import markdown
import codecs
import requests
import json
import re
from mod_parryc.models import *
from sqlalchemy import and_
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
  _ts_response = {}
  inline_data  = None
  project_size = 0
  if request.method == 'POST':
    # 0 = small
    # 1 = medium
    # 2 = large
    #
    request_id = request.json['request_id']
    interval_count = request.json['timeseries_interval_count']
    if 'request_project_size' in request.json:
      project_size = request.json['request_project_size']
    if 'request_inline_data' in request.json:
      inline_data = request.json['request_inline_data']

    updating_request = get_vps_request(request_id)
    if not updating_request:
      save_result = add_vps_request(request_id, project_size, False, [], interval_count)
    else:
      # pass through next condition
      save_result = {'status':True}

    if save_result['status']:
      # If request_inline_data is not set
      if inline_data is None:
        inline_data = _paas_projects_to_hours(_paas_get_projects_by_size(project_size))
      _ts_response = _paas_timeseries_request(inline_data, interval_count)
      update_result = edit_vps_request(request_id, _ts_response, interval_count)
  return jsonify(_ts_response)

@mod_parryc.route('/paas/retrieve/<request_id>', methods=['GET'], host=host)
def paas_lookup(request_id):
  timeseries_data = get_vps_request(request_id).timeseries_response.split(',')
  rounded = [round(float(td)/0.25) * 0.25 for td in timeseries_data]
  # zero-out weekdays
  output_data    = []
  weekly_output  = []
  _hours_to_move = 0
  # next Sunday
  current_date = date(2017,6,25)
  days = ["sunday","monday","tuesday","wednesday","thursday","friday","saturday"]
  for idx, el in enumerate(rounded):
    if idx % 7 == 0 and idx != 0:
      output_data.append({'row':weekly_output})
      weekly_output = []
    if idx in [0, 6, 7, 13, 14, 20, 21, 27, 28]:
      weekly_output.append({'value':0, 'day':days[idx % 7], 'date':current_date.isoformat()})
    else:
      weekly_output.append({'value':abs(el), 'day':days[idx % 7], 'date':current_date.isoformat()})

    current_date = current_date + timedelta(days=1)
  output_data.append({'row':weekly_output})
  return jsonify({'timeseries_data':output_data})

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
  if html == '<p>404</p>':
    return abort(404)
  return render_template('parryc/post.html',html=html)

def get_html(page):
  filepath = os.path.join(app.root_path, 'templates', page)
  try:
    input_file = codecs.open(filepath, mode="r", encoding="utf-8")
    text = input_file.read()
  except:
    text = '404'
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
  return ts_response.json()

def _paas_fill(log_dates):
  # Fill in 0s between dates
  padded = []
  for idx, t in enumerate(log_dates):
    if idx + 1 == len(log_dates):
      padded.append(t.hours_logged)
    else:
      _next = log_dates[idx + 1]
      delta = _next.log_date - t.log_date
      if delta.days == 1:
        padded.append(t.hours_logged)
      else:
        padded.append(t.hours_logged)
        padded.extend([0] * (delta.days - 1))
  return ",".join(map(str, padded))

def _paas_get_projects_by_size(size):
  low  = 0
  high = 1000
  bound_1 = 50
  bound_2 = 100
  if size == '0': # small
    high = bound_1
  if size == '1': # medium
    low = bound_1
    high = bound_2
  if size == '2': # large
    low = bound_2
  return Subprojects.query.filter(and_(Subprojects.hours_aggregate >= low, Subprojects.hours_aggregate < high)).all()

def _paas_projects_to_hours(projects):
  inline_data = []
  for project in projects:
    hours = get_hours(project.subproject)
    inline_data.append(_paas_fill(hours))
  joined = ",".join(inline_data)
  # compress the data by removing 0s, since timeseries doesn't detect patterns
  compressed = re.sub(r'(0,){3,}','0,', joined)
  # remove empty strings
  return re.sub(',+',',',compressed)
