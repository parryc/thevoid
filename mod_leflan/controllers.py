#!/usr/bin/env python
# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, redirect,\
                  url_for, flash, send_from_directory
from app import app
import os
import markdown
import codecs

mod_leflan = Blueprint('leflan.eu', __name__)

prod = True
if prod:
  host = 'leflan.eu'
else:
  host = 'localhost:5000'

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
                     ,'markdown.extensions.def_list'])

def _title(page):
  return page.replace('-',' ')

def _url(tag,page):
  return os.path.join('/r',tag_to_verb[tag],page)

def _add_filelist(category, html, show_tags=False):
  html += '<p><ul>'
  folder = os.path.join(os.getcwd(),'templates','leflan')
  for filename in sorted(os.listdir(folder),\
                  key=lambda _file:\
                      os.path.getmtime(os.path.join(folder,_file)),\
                  reverse=True):
    _parts = unicode(filename,'utf-8').split('_')
    if len(_parts) == 2 and 'md' in filename:
      page_name = _parts[1].replace('.md','').replace('-',' ')
      tag       = _parts[0]
      if not category or tag in verb_to_tag[category]:
        url       = _url(tag,page_name).replace(' ','-')
        if show_tags:
          html += u'<li><a href="%s">%s</a> <tag>%s</tag></li>' % (url, page_name, tag)
        else:
          html += u'<li><a href="%s">%s</a></li>' % (url, page_name) 
  html += '</ul></p>'
  return html

