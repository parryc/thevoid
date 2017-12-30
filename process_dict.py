import os
import xml.etree.ElementTree as ET
import unicodedata
import codecs
import re

count = 0

def sense(root, num, def_text):
  def example(sense, kz, en):
    kz = ' '.join(kz)
    en = ' '.join(en)
    cit = ET.Element('cit')
    cit.set('type', 'example')
    quote_kz = ET.SubElement(cit, 'quote')
    quote_kz.text = kz.strip()
    cit_trans = ET.SubElement(cit, 'cit')
    cit_trans.set('type', 'translation')
    cit_trans.set('xml:lang', 'en')
    quote_en = ET.SubElement(cit_trans, 'quote')
    quote_en.text = en.strip()
    sense.append(cit)

  def_text = re.sub(r'[1-9]+\.', '', def_text)
  grouping = def_text.split(';')
  def_text = grouping[0]
  # def_node = ET.fromstring('<def>{0}</def>'.format(def_text.strip()))

  sense = ET.SubElement(root, 'sense', attrib={'n':str(num)})
  def_node = ET.SubElement(sense, 'def')

  # when there is a semicolon in the definition
  # if len(grouping) > 1 and not re.findall(r'<kz>(.*?)</kz>', grouping[1]):
  #   def_text = '{0}; {1}'.format(def_text, grouping[1])
  #   grouping = grouping[2:]

  # preprocess to merge groups together
  ## TODO: process out _(see also <kz>..</kz>)_
  ## can appear within a sense and multiple
  ## ex. 1. .... (see also ...)
  ## (see also a, b)
  current_kz = []
  current_en = []
  current_see_also = []
  final_groups = []
  for group in grouping:
    see_also = re.findall(r'_\(see also <kz>(.*?)</kz>\)_', group)
    if see_also:
      current_see_also.extend(see_also[0].split(','))
      group = re.sub(r'_\(see also <kz>(.*?)</kz>\)_', '', group)

    kz = re.findall(r'<kz>(.*?)</kz>', group)
    if kz:
      final_groups.append((current_kz, current_en, current_see_also))
      current_kz = []
      current_en = []
      current_see_also = []
      group = re.sub(r'<kz>.*?</kz>','', group) # delete kz
      current_kz.extend(kz)
      current_en.append(group)
    else:
      current_en.append(group)
  if current_en:
    final_groups.append((current_kz, current_en, current_see_also))

  for kz, en, see_also in final_groups:
    if kz:
      example(sense, kz, en)
    else:
      def_text = ';'.join(en)
    if see_also:
      for sa in see_also:
        xr = ET.Element('xr', attrib={'type':'see'})
        ref = ET.SubElement(xr, 'ref')
        ref.text = sa
        sense.append(xr)

  def_node.text = def_text.strip()


def _entry_to_xml(filename, entry):
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
  entry = re.sub(KZ,r'<kz>\1</kz>',entry)
  # Code mark lemma
  if filename_length <= 2:
    len_re = re.compile('(.{'+str(filename_length)+'})')
    entry = re.sub(len_re,r'<kz>`\1`</kz>',entry,1) 
  else:
    entry = re.sub(KZ,r'`\1`',entry,1)
  # Make additional senses more distinct
  entry = re.sub(r'(\d+)',r'\n\1',entry)
  # Add another entry in front of the numbers so that Markdown recognizes it 
  # entry = re.sub(r'(\d+)',r'\n\1',entry,1)
  # Italicize parenthenticals
  entry = re.sub(r'([\(\[].+?[\)\]])',r'_\1_',entry)
  # Differentiate sense from examples
  # ## Multiple senses
  # if '1.' in entry:
  #   entry = re.sub(r'(\n.*?)(<kz>[а-ө~])',r'\1\n\2',entry)
  # else:
  #   entry = re.sub(r'(^.*?)(<kz>[а-ө~])',r'\1\n\2',entry)

  # replace “”
  entry = re.sub(r'“|”','"',entry)
  # replace ’
  entry = re.sub(r'’',"'",entry)
  # remove entry ending ;
  entry = re.sub(r'; ?\n','\n',entry)
  # Remove all new lines
  entry = re.sub(r'\n',' ',entry)
  # Remove extra spaces
  entry = re.sub(r' +',' ',entry)

  return entry

for filename in sorted(os.listdir(u'templates/words')):
  count += 1
  if count > 10:
    break

  if filename == '.DS_Store':
    continue

  # lemma
  # etym
  # usage
  # senses
  # homynyms (eventually)
  # see alsos (<re> node)
  root = ET.Element('entry')
  tree = ET.ElementTree(root)
  form = ET.SubElement(root, 'form')
  orth = ET.SubElement(form, 'orth')

  gramGrp = ET.SubElement(root, 'gramGrp')
  pos = ET.SubElement(gramGrp, 'pos')
  # OSX stored decomposed filenames
  filename = unicodedata.normalize('NFC', filename)

  path = u'templates/words/{}'.format(filename)
  with codecs.open(path,'r','utf-8') as in_file:
    content = in_file.read()

    ## should replace with tags instead of markdown
    ## need to indentify def vs. examples.
    # check for weird extra encodings like \xa0
    entry = _entry_to_xml(filename, content)
    usage = ''
    lemma = re.match(r'<kz>`(.*?)`</kz>', entry).group(1)
    orth.text = lemma
    entry = re.sub(r'<kz>`(.*?)`</kz>', '', entry).strip()

    # all entries which have a POS will have it for sure in the
    # 2nd position and possibly the 3rd (in the case of, e.g. "vbl. n.")
    words = entry.split(' ')
    pos_text = ''
    cutoff = 0
    if '.' in words[1]:
      pos_text += words[1][:-1]
      cutoff = 1
    if '.' in words[2]:
      pos_text += ' ' + words[2][:-1]
      cutoff = 2
    entry = ' '.join(words[cutoff:])
    pos.text = pos_text
    # pos_check = re.match(r'^([a-z]+\.)', entry)
    # # maybe this should be from a list?
    # if pos_check:
    #   pos_text = re.sub(r'\.', '', pos_check.group(1))
    #   pos.text = pos_text
    #   entry = re.sub('{0}\. '.format(pos_text), '', entry)

    entry = entry.strip()
    senses = re.findall(r'[1-9]+\. [^1-9]+', entry)
    # print(senses)
    if senses:
      for num, definition in enumerate(senses):
        sense(root, num + 1, definition)
    else:
      sense(root, 1, entry)

    # ET.dump(root)
    # check if filename already exists, if so make into a superentry
    tree.write(open(os.path.join('testing', lemma+'.xml'), 'w'), encoding="unicode")
    # etym = re.search(r'(\[.*?\])',content)
    # if etym:
    #   etym = etym.group(0)[1:-1]
    #   etyms.add(etym)
    # else:
    #   etym = ""

    # match (word.) to try to get "tags" for definitions
    # is it worth trying to tag the first а that has (...; colloq.)?
    # also try to get other inline tags like албасты (myth.) (fig.)
    # tag = re.search(r'(\([^ ]*?\.\))',content)
    # if tag:
    #   # remove ending period
    #   tag = tag.group(0)[1:-2]
    #   tags.add(tag)
    # else:
    #   tag = ""
