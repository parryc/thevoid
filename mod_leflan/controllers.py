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

@mod_leflan.route('/r/learns/<language>/dict', methods=['GET'], host=host)
def dictionary(language):
  page_dict       = 'leflan/%s.dict' % language
  filepath        = os.path.join(app.root_path, 'templates', page_dict).encode('utf-8')
  input_file_dict = codecs.open(filepath, mode="r", encoding="utf-8")
  dictionary      = []
  tag_list        = set()

  for row in input_file_dict:
    data    = row.split('\t')
    senses  = []
    _senses = data[1].split(u';')

    try:
      tags = data[2].split(',')
      for tag in tags:
        if len(tag.strip()) > 0:
          tag_list.add(tag.strip())
    except IndexError, e:
      tags = []

    try:
      extra = data[3].strip()
    except IndexError, e:
      extra = ''


    for _sense in _senses:
      _parts = _sense.split(u'␞')
      try:
        senses.append({
         'meaning':_parts[0]
        ,'example':_parts[1]
        })
      except IndexError, e:
        senses.append({
         'meaning':_parts[0]
        ,'example':''
        })

    entry = {
      'headword':data[0]
     ,'senses'  :senses
     ,'tags'    :tags
     ,'extra'   :extra
    } 
    dictionary.append(entry)

  dictionary = sorted(dictionary,key=lambda entry: entry['headword'])

  return render_template('leflan/dictionary.html',dictionary=dictionary
                         ,title=_title(language),tag_list=tag_list)

@mod_leflan.route('/r/learns/<language>/dict_dnu', methods=['GET'], host=host)
def dictionary_dnu(language):
  # Parse grammar file
  page_lang = 'leflan/language_%s.md' % language
  filepath = os.path.join(app.root_path, 'templates', page_lang).encode('utf-8')
  input_file_lang = codecs.open(filepath, mode="r", encoding="utf-8")

  declensions = {}
  rule_set    = {}
  rule_names  = {}
  rule_ends   = {}
  rule_pre    = {}
  processing  = False
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
      #If the POS of the rule set has not been seen before
      #Add it to the set of possible rules
      if _type not in rule_set.keys():
        rule_set[_type]   = []
        rule_names[_type] = []
        rule_ends[_type]  = []
        rule_pre[_type]   = []
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

      #After successfully scanning a rule
      #Add the table_data to the rule set dictionary
      #under the correct type 
      table_rows = table_rows[1:]
      for row in table_rows:
        cols = row.split('|')
        for idx, col in enumerate(cols):
          col = col.strip()
          if idx == 0:
            _name = col
            continue
          table_data[idx-1][_name] = _process_table_column(col)

      rule_set[_type].append(table_data)
      rule_names[_type].append(_endings)
      rule_ends[_type].append(_endings)
      rule_pre[_type].append(_pre)

      ## save name as type + endings?
      ## so then it can be recalled below, when processing the dict

    # if the first char is a dash, it's just table markup
    if processing and row[0] != '-':
      table = table + row

  page_dict = 'leflan/%s.dict' % language
  filepath = os.path.join(app.root_path, 'templates', page_dict).encode('utf-8')
  input_file_dict = codecs.open(filepath, mode="r", encoding="utf-8")
  dictionary = []
  for row in input_file_dict:
    data     = row.split('|')
    if len(data) < 3 or data[0].strip() == u'headword':
      continue

    # Dictionary schema
    headword = data[0].strip()
    sense    = data[1].strip()
    pos      = data[2].strip()

    if len(data) > 3:
      gender = data[3].strip()

    if len(data) > 4:
      tag    = data[4].strip()

    # If the root of the noun/verb is different
    # than the headword
    root = headword
    if len(data) > 5:
      root   = data[5].strip()

    # Find correct rule
    ## Search through rule_names by type and find the index of the
    ## set of endings 
    rule_found = False
    if pos in rule_names.keys():
      for _rule_idx, rule in enumerate(rule_names[pos]):
        # find correct ending
        if rule_found:
          continue
        ending_idx = -1
        stem = ''
        for _idx, _ending in enumerate(rule):
            _re = '%s$' % _ending
            if re.search(_re, root):
              ending_idx = _idx
              rule_idx   = _rule_idx
              stem       = re.sub(_re, '', root)
              rule_found = True

      if rule_found:
        _endings   = rule_ends[pos][rule_idx]
        _pre       = rule_pre[pos][rule_idx]
        table_data = rule_set[pos][rule_idx]

      stem = stem + _pre[ending_idx]
      declensions = []

      if rule_found:
        for data in table_data:
          # Nouns
          if pos == 'n':
            entry = {
              'name':data['name'],
              'type':'n',
              's'   :stem + data['_s._'][ending_idx],
              'p'   :stem + data['_p._'][ending_idx]
            }
            if '***' in entry['s']:
              entry['s'] = headword
            if '***' in entry['p']:
              entry['p'] = headword

            entry = _clean_entry(entry,language)
            declensions.append(entry)

          # Verbs
          if pos == 'v':
            entry = {
              'name':data['name'],
              'type':'v',
              'one' :stem + data['1'][ending_idx],
              'two' :stem + data['2'][ending_idx],
              'tre' :stem + data['3'][ending_idx]
            }

            entry = _clean_entry(entry,language)
            declensions.append(entry)

    # Senses appear as
    # translation␞sentence,translation␞repeat...
    sense_parts = sense.split(u'␞')
    sense = sense_parts[0]
    if len(sense_parts) > 1:
      examples = [ {'example':example.split(u';')[0],
                    'translation':example.split(u';')[1]}
                  for example in sense_parts[1:]]
    else:
      examples = []

    declensions = _set_declensions(declensions,pos,language)

    dictionary.append({
      'headword'   :headword,
      'sense'      :sense,
      'examples'   :examples,
      'pos'        :pos,
      'declensions':declensions
      })

    dictionary = sorted(dictionary,key=lambda entry: entry['headword'])

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
    if entry['type'] == 'n':
      entry['s'] = entry['s'].replace(u'iį',u'į')
      entry['s'] = entry['s'].replace(u'iy',u'y')

  return entry

def _set_declensions(declensions,pos,language):
  if language == 'lithuanian' and (pos == 'a' or pos == 'adv'):
    return []

  return declensions

