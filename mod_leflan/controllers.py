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

testing = app.config['LEFLAN_TEST']
if not testing:
  host   = 'leflan.eu'
  if not (app.config['LEFLAN_TEST'] or app.config['PARRYC_TEST'] or app.config['CORBIN_TEST']):
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
 ,'through-writing':'learns'
}

verb_to_tag = {
  'learns' : ['language','through-reading','through-writing']
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
  return render_template('leflan/post.html',html=html,title='recent updates',t=_t('recent updates'))

@mod_leflan.route('/r/<category>', methods=['GET'], host=host)
def category(category):
  html = _add_filelist(category,'')
  return render_template('leflan/category.html',html=html,category=category,title=_title(category),t=_t(category))

@mod_leflan.route('/r/learns/<language>', methods=['GET'], host=host)
def language(language):
  page = 'leflan/language_%s.md' % language
  html = get_html(page)
  return render_template('leflan/post.html',html=html,title=_title(language),t=_t(language))

@mod_leflan.route('/r/learns/<language>/through-<learning_type>', methods=['GET'], host=host)
def through_index(language, learning_type):
  page = 'leflan/through-%s_%s/index.md' % (learning_type, language)
  html = get_html(page)
  title = 'learn %s through %s' % (language, learning_type)
  return render_template('leflan/post.html',html=html,title=_title(title),t=_t(title))

@mod_leflan.route('/r/learns/<language>/through-<learning_type>/<post>', methods=['GET'], host=host)
def through_post(language, learning_type, post):
  page = 'leflan/through-%s_%s/%s.md' % (learning_type, language, post)
  html = get_html(page)
  title = 'learn %s through %s: %s' % (learning_type, language, post.replace('_',' '))
  return render_template('leflan/post.html',html=html,title=_title(title),t=_t(title))

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
        'headword':row
       ,'senses'  :[]
       ,'tags'    :['error']
       ,'extra'   :''
      }
      tag_list.add('error')
      dictionary.append(entry)
      continue

    try:
      tags = list(map(str.strip, data[2].split(',')))
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

    if '（' in data[0]:
      matches = re.match(r'(.*?)\[(.+?)\]（([\u3040-\u3096]+?)）(.*)', data[0])
      headword = '{0}<ruby><rb>{1}</rb><rt>{2}</rt></ruby>{3}'.format(matches.group(1),
                                                                      matches.group(2),
                                                                      matches.group(3),
                                                                      matches.group(4))
    else:
      headword = data[0]

    entry = {
      'headword':headword
     ,'senses'  :senses
     ,'tags'    :tags
     ,'extra'   :extra
    }
    dictionary.append(entry)

  # remove the beginning html which messes up sorting for Japanese words
  dictionary = sorted(dictionary,key=lambda entry: entry['headword'].replace('<ruby><rb>',''))
  tag_list   = sorted(tag_list)

  return render_template('leflan/dictionary.html',dictionary=dictionary
                         ,title=_title(language),tag_list=tag_list)

@mod_leflan.route('/r/reads/<book>', methods=['GET'], host=host)
def book(book):
  page = 'leflan/books_%s.md' % book
  html = get_html(page)
  return render_template('leflan/post.html',html=html,title=_title(book),t=_t(book))

def get_html(page):
  filepath = os.path.join(app.root_path, 'templates', page)
  git_page = os.path.join(folder, page.split('/')[-1])
  input_file = codecs.open(filepath, mode="r", encoding="utf-8")
  text = input_file.read()
  print(page)
  if page == 'leflan/index.md':
    time = repo.git.log('-n 1','--format=%ci')
  elif 'through-reading' in page or 'through-writing' in page:
    path_parts = page.split('/')
    if 'index.md' in page:
      # go up to the folder level to get the most recent subpage's change
      # page_parts = page.split('/')
      git_page = os.path.join(folder, path_parts[-2])
      time = repo.git.log('-n 1','--format=%ci','--', git_page)
    else:
      git_page = os.path.join(folder, path_parts[-2], path_parts[-1])
      time = repo.git.log('-n 1','--format=%ci','--', git_page)
  else:
    time = repo.git.log('-n 1','--format=%ci','--', git_page)
  time = ' '.join(time.split(' ')[0:2])
  text = '_Last updated {0}_\n\n'.format(time) + text
  return markdown.markdown(text,
          extensions=['markdown.extensions.nl2br'
                     ,'markdown.extensions.toc'
                     ,'markdown.extensions.tables'
                     ,'markdown.extensions.def_list'
                     ,'markdown.extensions.abbr'
                     ,'markdown.extensions.footnotes'
                     ,'mod_leflan.furigana'
                     ,BracketTable()
                     ,'doctor_leipzig.doctor_leipzig'
                     ,'mod_leflan.examples'])

def _title(page):
  return page.replace('-',' ')

def _t(t):
  return 'le_flaneur | {0}'.format(_title(t))

def _url(tag,page):
  if tag == 'through-reading':
    return os.path.join('/r',tag_to_verb[tag],page,'through-reading')
  if tag == 'through-writing':
    return os.path.join('/r',tag_to_verb[tag],page,'through-writing')
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
      if page_name in ['hebrew', 'indonesian', 'greenlandic']:
        continue

      if not category or tag in verb_to_tag[category]:
        url = _url(tag,page_name).replace(' ','-')
        if tag == 'through-reading':
          page_name += ' through reading'
        if tag == 'through-writing':
          page_name += ' through writing'
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

