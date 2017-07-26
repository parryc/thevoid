#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals
from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.util import etree
import re

GROUPER = r'("|\'((?!\s)|^)).+?("|(?=\').*?"|\'((?=\s)|$))|[^\s]+'
ASSUME_TITLE = True

class LeipzigProcessor(BlockProcessor):
  def test(self, parent, block):
    """
      Test if valid BracketTable.
    """
    HEADER = '--GLOSS--'
    FOOTER = '--ENDGLOSS--'
    rows = [row.strip() for row in block.split('\n')]
    return HEADER == rows[0] and rows[-1] == FOOTER

  def run(self, parent, blocks):
    """ Parse a table block and build table. """
    block = blocks.pop(0).split('\n')
    header = block[0].strip()[1:-1]
    rows = block[1:-1]
    groups = [self._create_grouping(row) for row in rows]
    max_len = len(max(groups, key=len))
    # fill to full size
    filled = [group + [''] * (max_len - len(group)) for group in groups]
    zipped_rows = zip(filled)
    tbody_wrapper = self._build_table(parent, _class='leipzig-table')

    for idx, row in enumerate(filled):
      tr_wrapper = etree.SubElement(tbody_wrapper, 'tr')
      tr_wrapper.set('class','leipzig-' + self._get_line_class(idx))
      td_colspan = 1
      full_span = False

      if idx == 0:
        num_td = etree.SubElement(tr_wrapper, 'td')
        num = etree.SubElement(num_td, 'span')
        num.set('class','leipzig-num')
        if ASSUME_TITLE:
          td = etree.SubElement(tr_wrapper, 'td')
          td.text = ' '.join([self._beautify(item) for item in row])
          td.set('colspan', str(max_len))
      else:
        etree.SubElement(tr_wrapper, 'td')

      for item in row:
        # If ASSUME_TITLE is on, don't process the first
        # row of the gloss block
        if ASSUME_TITLE and idx == 0:
          continue

        if item == '{!}':
          full_span = True
          td_colspan = max_len
          continue

        if item not in ['{m}', '{b}', '{!}']:
          td = etree.SubElement(tr_wrapper, 'td')
          # span = etree.SubElement(td, 'span')
          td.text = self._beautify(item)
          if td_colspan != 1:
            td.set('colspan', str(td_colspan))
            td_colspan = 1
          if full_span:
            break

        if item == '{m}':
          td_colspan += 1

        if item == '{b}':
          td = etree.SubElement(tr_wrapper, 'td')

      if td_colspan != 1:
        td.set('colspan', str(td_colspan))

    # parent_bracket = etree.SubElement(tr_wrapper, 'td')
    # parent_text = etree.SubElement(tr_wrapper, 'td')

    # tbody_rows = self._build_table(parent_text)
    # for row in rows:
    #   self._build_row(row, tbody_rows, longest)

    # tbody_bracket = self._build_table(parent_bracket)
    # tr = etree.SubElement(tbody_bracket, 'tr')
    # td_right = etree.SubElement(tr,'td')
    # td_right.set('rowspan', str(rowspan))
    # span_text = etree.SubElement(td_right, 'span')
    # span_text.text = header
    # span_text.set('class', 'bracket_table bracket_text')
    # td_bracket = etree.SubElement(tr,'td')
    # td_bracket.set('rowspan', str(rowspan))
    # span_bracket = etree.SubElement(td_bracket, 'span')
    # span_bracket.text = '{'
    # span_bracket.set('class', 'bracket_table bracket')
    # span_bracket.set('style', 'font-size: %sem;' % (rowspan + 2))

  def _build_row(self, row, parent, longest):
    """ Given a row of text, build table cells. """
    tr = etree.SubElement(parent, 'tr')
    tag = 'td'
    cells = row.split('|')
    # similar to the Markdown.Tables extension
    # make sure each row is the same size
    for i, a in enumerate(longest.split('|')):
      c = etree.SubElement(tr, tag)
      try:
        c.text = cells[i].strip()
      except IndexError:
        c.text = ""

  def _build_table(self, parent, _class=None):
    table = etree.SubElement(parent, 'table')
    if _class:
      table.set('class', _class)
    thead = etree.SubElement(table, 'thead')
    tbody = etree.SubElement(table, 'tbody')
    return tbody

  def _create_grouping(self, row):
    grouping = []
    while re.match(GROUPER, row):
      group = re.match(GROUPER, row)
      row = row[(group.end(0) + 1):]
      grouping.append(group.group(0))
    return grouping

  def _beautify(self, text):
    # escape brackets
    text = re.sub(r'<','&lt;',text)
    text = re.sub(r'>','&gt;',text)
    # remove quotes around long strings
    text = re.sub(r'(^(\'|"))|((\'|")$)','',text)
    # Set morpheme (for small caps!)
    text = re.sub(r'\{','<span class="leipzig-morpheme">',text)
    text = re.sub(r'\}','</span>',text)
    # Tildes look bad in Computer Modern
    text = re.sub(r'~','<span class="leipzig-tilde">~</span>',text)
    return '<span>'+text+'</span>'

  def _get_line_class(self, idx):
    classes = ['source', 'morphemes', 'translation', 'translation']
    if idx < len(classes):
      return classes[idx]
    return ''

class Leipzig(Extension):
  def extendMarkdown(self, md, md_globals):
    # The normal table extension uses '<hashheader', so why not
    md.parser.blockprocessors.add('doctor_leipzig',
                                   LeipzigProcessor(md.parser),
                                   '<hashheader')
    