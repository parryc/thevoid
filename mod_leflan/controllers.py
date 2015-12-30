#!/usr/bin/env python
# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, redirect,\
                  url_for, flash, send_from_directory
from app import app
from git import Repo
import os
import markdown
import codecs
import re

mod_leflan = Blueprint('leflan.eu', __name__)

testing = app.config['LEFLAN_TEST']
if not testing:
  host   = 'leflan.eu'
  repo   = Repo('~/vcs/git/default.git')
  folder = os.path.join('templates','leflan')
else:
  host   = 'localhost:5000'
  repo   = Repo(os.getcwd())
  folder = os.path.join(os.getcwd(),'templates','leflan')

############################
# The Flaneur's dictionary #
############################
tag_to_verb = {
  'language':'learns'
 ,'books'   :'reads'
}

verb_to_tag = {
  'learns' : ['language']
 ,'reads'  : ['books']
}

##########
# Routes #
##########

@mod_leflan.route('/favicon.ico', host=host)
def favicon():
  return send_from_directory(os.path.join(app.root_path, 'static'),
                             'favicon.ico', mimetype='image/vnd.microsoft.icon')
@mod_leflan.route('/css/<path:css>', host=host)
def css(css):
  if 'fonts' in css:
    return send_from_directory(os.path.join(app.root_path, 'static/css'), css)
  else:
    return send_from_directory(os.path.join(app.root_path, 'static/gen'), css)

@mod_leflan.route('/images/<folder>/<image>', host=host)
def image_with_folder(folder, image):
  return send_from_directory(os.path.join(app.root_path, 'static/images', folder), image)

@mod_leflan.route('/images/<image>', host=host)
def image(image):
  return send_from_directory(os.path.join(app.root_path, 'static/images'), image)


@mod_leflan.route('/', methods=['GET'], host=host)
def index():
  return redirect(url_for('.r'))
  
@mod_leflan.route('/r', methods=['GET'], host=host)
def r():
  page = 'leflan/index.md'
  html = get_html(page)
  html = _add_filelist('',html,show_tags=True)
  return render_template('leflan/post.html',html=html,title='recent updates')

@mod_leflan.route('/r/<category>', methods=['GET'], host=host)
def category(category):
  html = _add_filelist(category,'')
  return render_template('leflan/category.html',html=html,category=category)

@mod_leflan.route('/r/learns/<language>', methods=['GET'], host=host)
def language(language):
  page = 'leflan/language_%s.md' % language
  html = get_html(page)
  return render_template('leflan/post.html',html=html,title=_title(language))

@mod_leflan.route('/r/learns/<language>/dict', methods=['GET'], host=host)
def dictionary(language):
  # Parse grammar file
  page_lang = 'leflan/language_%s.md' % language
  filepath = os.path.join(app.root_path, 'templates', page_lang).encode('utf-8')
  input_file_lang = codecs.open(filepath, mode="r", encoding="utf-8")

  declensions = {}
  processing = False
  for row in input_file_lang:
    if 'BEGIN' in row:
      _id = re.match('<!-- BEGIN:(.+)-->',row).group(1).strip()
      table = ''
      processing = True
      continue
    if 'ENDING' in row:
      _endings = _dict_process_attributes(row,'ENDING')
      continue
    if 'PRE' in row:
      _pre = _dict_process_attributes(row,'PRE')
      continue
    if 'TYPE' in row:
      _type = _dict_process_attributes(row,'TYPE')[0]
      continue
    if 'END' in row:
      processing = False
      table_data = []
      table_rows = table.split('\n')
      
      cols = table_rows[0].split('|')
      for idx, col in enumerate(cols):
        if idx == 0:
          continue
        table_data.append({
          'name':col.strip()
          })

      table_rows = table_rows[1:]
      for row in table_rows:
        cols = row.split('|')
        for idx, col in enumerate(cols):
          col = col.strip()
          if idx == 0:
            _name = col
            continue
          table_data[idx-1][_name] = _process_table_column(col)

    # if the first char is a dash, it's just table markup
    if processing and row[0] != '-':
      table = table + row

  page_dict = 'leflan/%s.dict' % language
  filepath = os.path.join(app.root_path, 'templates', page_dict).encode('utf-8')
  input_file_dict = codecs.open(filepath, mode="r", encoding="utf-8")
  dictionary = []
  for row in input_file_dict:
    data     = row.split('|')
    if len(data) < 3:
      continue
    headword = data[0].strip()
    sense    = data[1].strip()
    pos      = data[2].strip()

    # find correct ending
    _ending_idx = -1
    stem = ''
    for idx, _ending in enumerate(_endings):
      _re = '%s$' % _ending
      if re.search(_re, headword):
        _ending_idx = idx
        stem = re.sub(_re, '', headword)

    stem = stem + _pre[_ending_idx]
    declensions = []

    for data in table_data:
      # Nouns
      if _type == 'n':
        entry = {
          'name':data['name'],
          's'   :stem + data['_s._'][_ending_idx],
          'p'   :stem + data['_p._'][_ending_idx]
        }
        if '***' in entry['s']:
          entry['s'] = headword
        if '***' in entry['p']:
          entry['p'] = headword

        entry = _clean_entry(entry,language)
        declensions.append(entry)

    #if language == 'lithuanian':
    dictionary.append({
      'headword'   :headword,
      'sense'      :sense,
      'pos'        :pos,
      'type'       :_type,
      'declensions':declensions
      })

  return render_template('leflan/dictionary.html',dictionary=dictionary
                         ,title=_title(language))

@mod_leflan.route('/r/reads/<book>', methods=['GET'], host=host)
def book(book):
  page = 'leflan/books_%s.md' % book
  html = get_html(page)
  return render_template('leflan/post.html',html=html,title=_title(book))

def get_html(page):
  filepath = os.path.join(app.root_path, 'templates', page).encode('utf-8')
  input_file = codecs.open(filepath, mode="r", encoding="utf-8")
  text = input_file.read()
  return markdown.markdown(text,
          extensions=['markdown.extensions.nl2br'
                     ,'markdown.extensions.toc'
                     ,'markdown.extensions.tables'
                     ,'markdown.extensions.def_list'
                     ,'markdown.extensions.abbr'
                     ,'markdown.extensions.footnotes'])

def _title(page):
  return page.replace('-',' ')

def _url(tag,page):
  return os.path.join('/r',tag_to_verb[tag],page)

def _add_filelist(category, html, show_tags=False):
  html += '<p><ul>'
  for filename in sorted(os.listdir(folder),\
                  key=lambda _file:\
                      repo.git.log('-n 1','--format=%ci','--',os.path.join(folder,_file)),\
                  reverse=True):

    _parts = unicode(filename,'utf-8').split('_')
    if len(_parts) == 2 and 'md' in filename:
      page_name = _parts[1].replace('.md','').replace('-',' ')
      tag       = _parts[0]
      if not category or tag in verb_to_tag[category]:
        url = _url(tag,page_name).replace(' ','-')
        if show_tags:
          html += u'<li><a href="%s">%s</a> <tag>%s</tag></li>' % (url, page_name, tag)
        else:
          html += u'<li><a href="%s">%s</a></li>' % (url, page_name) 
  html += '</ul></p>'
  return html

def _dict_process_attributes(row,attribute):
  attribute_id = '<!-- %s:(.+)-->' % attribute
  _attributes = re.match(attribute_id,row).group(1).strip()
  _attributes = _attributes.replace(' ','').replace(u'∅',u'').split(',')
  return _attributes

def _process_table_column(col):
  """
    Column data comes in the form -xyz or -xyz/abc/def.  If there
    is only one example, then it applies to all endings. If there
    are multiples (i.e. slashes exist), then the correct ending uses
    the ending index. For example, if the word had ending type 1, it would
    have the ending "abc" in the example above.

    This processing creates a list to be easily appended to the stem once
    the ending number is known.
  """

  raw = col.replace('-','').replace(u'∅',u'')
  raw = re.sub(r'<sup>.*?</sup>','',raw)
  ending_list = raw.split('/')
  if len(ending_list) == 1:
    # yes 3 is a magic number. I don't know how many possible endings
    # there will be.
    ending_list = ending_list * 3

  return ending_list

def _clean_entry(entry,language):
  ######
  # LT #
  ######
  if language == 'lithuanian':
  # Noun declensions 1, -as/is/ys
  # In the ACC/LOC singular, the ending for is/ys does not use
  # the extended stem, because iį and iy are not valid.
    entry['s'] = entry['s'].replace(u'iį',u'į')
    entry['s'] = entry['s'].replace(u'iy',u'y')

  return entry

