from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.util import etree
import re

BRACKET_TABLE = r'\{.*\}(.*?\n)+.*?\{/\}'

class BracketTableProcessor(BlockProcessor):
  def test(self, parent, block):
    """
      Test if valid BracketTable.
    """
    HEADER = re.compile(r'^\{.*?\}$')
    FOOTER = u'{/}'
    rows = [row.strip() for row in block.split('\n')]
    return HEADER.match(rows[0]) and rows[-1] == FOOTER

  def run(self, parent, blocks):
    """ Parse a table block and build table. """
    block = blocks.pop(0).split('\n')
    header = block[0].strip()[1:-1]
    rows = block[1:-1]
    rowspan = len(rows)
    longest = max(rows, key=lambda x: len(x.split('|')))
    tbody_wrapper = self._build_table(parent, _class='bracket_table')
    tr_wrapper = etree.SubElement(tbody_wrapper, 'tr')

    parent_bracket = etree.SubElement(tr_wrapper, 'td')
    parent_text = etree.SubElement(tr_wrapper, 'td')

    tbody_rows = self._build_table(parent_text)
    for row in rows:
      self._build_row(row, tbody_rows, longest)

    tbody_bracket = self._build_table(parent_bracket)
    tr = etree.SubElement(tbody_bracket, 'tr')
    td_right = etree.SubElement(tr,'td')
    td_right.set('rowspan', str(rowspan))
    span_text = etree.SubElement(td_right, 'span')
    span_text.text = header
    span_text.set('class', 'bracket_table bracket_text')
    td_bracket = etree.SubElement(tr,'td')
    td_bracket.set('rowspan', str(rowspan))
    span_bracket = etree.SubElement(td_bracket, 'span')
    span_bracket.text = '{'
    span_bracket.set('class', 'bracket_table bracket')
    span_bracket.set('style', 'font-size: %sem;' % (rowspan + 2))

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

class BracketTable(Extension):
  def extendMarkdown(self, md, md_globals):
    # The normal table extension uses '<hashheader', so why not
    md.parser.blockprocessors.add('bracket_table',
                                   BracketTableProcessor(md.parser),
                                   '<hashheader')
    