#!/usr/bin/env python
# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, redirect,\
                  url_for, flash, send_from_directory
from app import app
from git import Repo
from bracket_table.bracket_table import BracketTable
# from doctor_leipzig import Leipzig
import os
import markdown
import codecs
import re

mod_leflan = Blueprint('leflan.eu', __name__)

testing = (app.config['LEFLAN_TEST'] or app.config['PARRYC_TEST'])
if not testing:
  host   = 'leflan.eu'
  repo   = Repo('/srv/data/vcs/git/default.git')
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
 ,'through-reading':'learns'
}

verb_to_tag = {
  'learns' : ['language','through-reading']
 ,'reads'  : ['books']
}

##########
# Routes #
##########

@mod_leflan.route('/favicon.ico', host=host)
def favicon():
  return send_from_directory(os.path.join(app.root_path, 'static'),
                             'favicon.ico', mimetype='image/vnd.microsoft.icon')

@mod_leflan.route('/robots.txt', host=host)
def robots():
  return render_template('robots.txt')

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

@mod_leflan.route('/r/learns/<language>/through-reading', methods=['GET'], host=host)
def through_reading_index(language):
  page = 'leflan/through-reading_%s/index.md' % language
  html = get_html(page)
  title = 'learn %s through reading' % language
  return render_template('leflan/post.html',html=html,title=_title(title))

@mod_leflan.route('/r/learns/<language>/through-reading/<post>', methods=['GET'], host=host)
def through_reading_post(language, post):
  page = 'leflan/through-reading_%s/%s.md' % (language, post)
  html = get_html(page)
  title = 'learn %s through reading: %s' % (language, post.replace('_',' '))
  return render_template('leflan/post.html',html=html,title=_title(title))

@mod_leflan.route('/r/learns/<language>/dict', methods=['GET'], host=host)
def dictionary(language):
  page_dict       = 'leflan/%s.dict' % language
  filepath        = os.path.join(app.root_path, 'templates', page_dict).encode('utf-8')
  input_file_dict = codecs.open(filepath, mode="r", encoding="utf-8")
  dictionary      = []
  tag_list        = set()

  for row in input_file_dict:
    try:
      data    = row.split('\t')
      senses  = []
      _senses = data[1].split(u';')
    except:
      entry = {
        'headword':unicode(row)
       ,'senses'  :[]
       ,'tags'    :['error']
       ,'extra'   :''
      }
      tag_list.add('error')
      dictionary.append(entry)
      continue

    try:
      from string import strip
      tags = map(strip, data[2].split(','))
      for tag in tags:
        if len(tag) > 0:
          tag_list.add(tag)
    except IndexError:
      tags = []

    try:
      extra = data[3].strip()
    except IndexError:
      extra = ''


    for _sense in _senses:
      _parts    = _sense.split(u'␞')

      try:
        senses.append({
         'meaning':_parts[0]
        ,'example':_parts[1]
        ,'english':_parts[2]
        })
      except IndexError:
        senses.append({
         'meaning':_parts[0]
        ,'example':''
        ,'english':''
        })

    entry = {
      'headword':data[0]
     ,'senses'  :senses
     ,'tags'    :tags
     ,'extra'   :extra
    } 
    dictionary.append(entry)

  dictionary = sorted(dictionary,key=lambda entry: entry['headword'])
  tag_list   = sorted(tag_list)

  return render_template('leflan/dictionary.html',dictionary=dictionary
                         ,title=_title(language),tag_list=tag_list)

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
                     ,'markdown.extensions.footnotes'
                     ,'mod_leflan.furigana'
                     ,BracketTable()
                     ,'doctor_leipzig.doctor_leipzig'])

def _title(page):
  return page.replace('-',' ')

def _url(tag,page):
  if tag == 'through-reading':
    return os.path.join('/r',tag_to_verb[tag],page,'through-reading')
  return os.path.join('/r',tag_to_verb[tag],page)

def _add_filelist(category, html, show_tags=False):
  html += '<p><ul>'
  for filename in sorted(os.listdir(folder),\
                  key=lambda _file:\
                      repo.git.log('-n 1','--format=%ci','--',os.path.join(folder,_file)),\
                  reverse=True):
    _parts = filename.split('_')
    # only list files which have been tagged
    if len(_parts) == 2 and _parts[0] != '.DS':
      tag       = _parts[0]
      page_name = _parts[1].replace('.md','').replace('-',' ')

      if not category or tag in verb_to_tag[category]:
        url = _url(tag,page_name).replace(' ','-')
        if tag == 'through-reading':
          page_name += ' through reading'
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
    if entry['type'] == 'n':
      entry['s'] = entry['s'].replace(u'iį',u'į')
      entry['s'] = entry['s'].replace(u'iy',u'y')

  return entry

def _set_declensions(declensions,pos,language):
  if language == 'lithuanian' and (pos == 'a' or pos == 'adv'):
    return []

  return declensions

