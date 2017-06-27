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
    header = block[0].strip()
    rows = block[1:-1]
    rowspan = len(rows)
    longest = max(rows, key=lambda x: len(x.split('|')))
    print(longest)
    table = etree.SubElement(parent, 'table')
    thead = etree.SubElement(table, 'thead')
    tbody = etree.SubElement(table, 'tbody')
    for row in rows:
      self._build_row(row, tbody, longest)

    table_bracket = etree.SubElement(parent, 'table')
    thead_bracket = etree.SubElement(table_bracket, 'thead')
    tbody_bracket = etree.SubElement(table_bracket, 'tbody')
    tr = etree.SubElement(tbody_bracket, 'tr')
    td_bracket = etree.SubElement(tr,'td')
    td_bracket.set('rowspan', str(rowspan))
    span_bracket = etree.SubElement(td_bracket, 'span')
    span_bracket.text = '}'
    td_right = etree.SubElement(tr,'td')
    td_right.set('rowspan', str(rowspan))
    td_right.text = header

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

class BracketTable(Extension):
  def extendMarkdown(self, md, md_globals):
    # The normal table extension uses '<hashheader', so why not
    md.parser.blockprocessors.add('bracket_table',
                                   BracketTableProcessor(md.parser),
                                   '<hashheader')
    