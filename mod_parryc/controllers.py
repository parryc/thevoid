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
# from whoosh.qparser import QueryParser
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

# ---------
#  KZ Dict
# ---------

@mod_parryc.route('/kz/search', methods=['GET', 'POST'], host=host)
def dict_search_index():
  if request.method == 'POST':
    return redirect(url_for('.dict_search', search=request.form['search']))
  return render_template('parryc/dictionary_search.html')

@mod_parryc.route('/kz/<lemma>', methods=['GET'], host=host)
def dict_lemma(lemma):
  page = 'words/%s.txt' % lemma
  html = get_html(page, dictionary_entry=True)
  if html == '<p>404</p>':
    return abort(404)
  return render_template('parryc/post.html',html=html)

@mod_parryc.route('/kz/search/<search>', methods=['GET'], host=host)
def dict_search(search):
  hits = []
  with ix.searcher() as searcher:
    # Default to prefix search
    query = QueryParser('title', ix.schema).parse(search)
    results = searcher.search(query)
    for result in results:
      title = re.sub(r'-\d','',result['title'])
      summary = markdown.markdown(_clean_dictionary(result['title'] + '.txt', result['summary']))
      link = '<a href="/kz/{0}">{0}</a>'.format(title)
      summary = re.sub(r'<code>.*?</code>',link,summary)
      hits.append({
        'title':title
       ,'summary':summary
        })

  return render_template('parryc/dictionary_results.html',hits=hits)

# ---------
#  End KZ Dict
# ---------

def get_html(page, dictionary_entry=False):
  filepath = os.path.join(app.root_path, 'templates', page)
  try:
    input_file = codecs.open(filepath, mode="r", encoding="utf-8")
    text = input_file.read()
  except:
    text = '404'
  if dictionary_entry:
    text = _clean_dictionary(page.split('/')[1], text)
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

def _clean_dictionary(filename, entry):
  KZ = r'([а-өА-Ө~«-][а-өА-Ө ~–?\.!,«»-]+[а-өА-Ө~?\.!,»])'
  # ай-ай-күні
  # doesn't seem to want to catch things with a lot of dashes

  # Make sure that it's composed correctly
  filename = unicodedata.normalize('NFC', filename)
  # Make sure there is always a space in front of parentheticals
  entry = re.sub(r'\(',' (',entry)
  # The regex above doesn't support single word lemmas
  filename_length = len(re.sub(r'-\d','',filename[:-4]))
  # Bold Kazakh words/phrases
  entry = re.sub(KZ,r'**\1**',entry)
  # Code mark lemma
  if filename_length <= 2:
    len_re = re.compile(u'(.{'+unicode(filename_length)+u'})')
    entry = re.sub(len_re,r'**`\1`**',entry,1) 
  else:
    entry = re.sub(KZ,r'`\1`',entry,1)
  # Make additional senses more distinct
  entry = re.sub(r'(\d+)',r'\n\1',entry)
  # Add another entry in front of the numbers so that Markdown recognizes it 
  entry = re.sub(r'(\d+)',r'\n\1',entry,1)
  # Italicize parenthenticals
  entry = re.sub(r'([\(\[].+?[\)\]])',r'_\1_',entry)
  # Differentiate sense from examples
  ## Multiple senses
  if '1.' in entry:
    entry = re.sub(r'(\n.*?)(\*\*[а-ө~])',r'\1\n\2',entry)
  else:
    entry = re.sub(r'(^.*?)(\*\*[а-ө~])',r'\1\n\2',entry)

  # replace “”
  entry = re.sub(r'“|”','"',entry)
  # remove entry ending ;
  entry = re.sub(r'; ?\n','\n',entry)
  # Remove extra spaces
  entry = re.sub(r' +',' ',entry)
  return entry
