import os
import xml.etree.ElementTree as ET
import unicodedata
import codecs
import re

count = 0

def sense(root, num, def_text):
  def example(sense, kz, en):
    kz = ' '.join(kz)
    kz = re.sub(r'\|(.*?)\|', r'(or \1)', kz)
    kz = re.sub(r'【', '(', kz)
    kz = re.sub(r'】', ')', kz)


    en = ' '.join(en)
    en = re.sub(r'◊|□', '', en) # still not entirely sure what these are used for
    en = re.sub(r' +', ' ', en)
    en = re.sub(r'\.$', '', en)
    en = re.sub(r'</?kz>', '', en)

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

  def_text = re.sub(r'[1-9]+\.', '', def_text) # remove sense number
  grouping = def_text.split(';')
  def_text = grouping[0]

  sense = ET.SubElement(root, 'sense', attrib={'n':str(num)})
  def_node = ET.SubElement(sense, 'def')

  # preprocess to merge groups together
  current_kz = []
  current_en = []
  current_see_also = []
  current_usg = []
  final_groups = []
  for group in grouping:

    ######
    # XR #
    ######

    see_also = re.findall(r'\(see also <kz>(.*?)</kz>\)', group)
    if see_also:
      current_see_also.extend(see_also[0].split(','))
      group = re.sub(r'\(see also <kz>(.*?)</kz>\)', '', group)

    #######
    # USG #
    #######

    usgs = re.findall(r'\(([a-z, ]+\.)\)', group)
    if usgs:
      for usg in usgs:
        # some object, something, literal, figurative
        if usg not in ['s.o.', 'sth.', 'lit.', 'fig.', 'folk.']:
          current_usg.extend(usg.split(','))
          group = re.sub(re.compile('\('+usg+'\)'), '', group)

    #######
    # CIT #
    #######

    # all citations should have an ~ 
    kz = re.findall(r'<kz>(.*?~.*?)</kz>', group)
    if kz:
      final_groups.append(
        (current_kz, current_en, current_see_also, current_usg)
      )
      current_kz = []
      current_en = []
      current_see_also = []
      current_usg = []
      group = re.sub(r'<kz>.*?</kz>','', group) # delete kz
      current_kz.extend(kz)
      current_en.append(group)
    else:
      current_en.append(group)
  if current_en:
    final_groups.append((current_kz, current_en, current_see_also, current_usg))

  for kz, en, see_also, usg in final_groups:
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

    if usg:
      for u in usg:
        # maybe add type attrib for domain classification
        usg = ET.Element('usg')
        usg.text = u[:-1]
        sense.append(usg)

  def_text = re.sub(r'</?kz>', '', def_text)
  def_node.text = re.sub(r'\.$','',def_text.strip())


def _entry_to_xml(filename, entry):
  KZ = r'([\|【а-өА-Ө~«-][\|【】а-өА-Ө ~–?\.!,«»-]+[а-өА-Ө~?\.!,»\|】])'
  OR = r'\(or ([а-өА-Ө, ~]+)\)'
  REL = r'\(of ([а-өА-Ө, ]+)\)'

  # Clean up "(or/of ...)s" so they get included in <kz> tags
  entry = re.sub(OR, r'|\1|', entry)
  entry = re.sub(REL, r'+\1+', entry)

  # replace two spaces with a semi-colon
  # it looks like half of the entries got messed up some how?
  entry = re.sub(r'  ','; ',entry)

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


test_words = ['түр.txt', 'шаң.txt', 'абалау.txt', 'абажадай.txt', 'бәсею.txt', 'а.txt', 'а-2.txt', 'аба.txt', 'адал.txt', 'абақты.txt', 'адамгершілік-гі.txt', 'адамдық-ғы.txt', 'ор.txt']
seen_lemmas = []
#sorted(os.listdir(u'templates/words'))
for filename in test_words:
  duplicate_lemma = False
  if filename == '.DS_Store':
    continue

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

    # check for weird extra encodings like \xa0
    entry = _entry_to_xml(filename, content)
    usage = ''
    lemma = re.match(r'<kz>`(.*?)`</kz>', entry).group(1)
    orth.text = lemma
    duplicate_lemma = (lemma in seen_lemmas)
    seen_lemmas.append(lemma)

    if 'гі' in filename or 'ғы' in filename:
      ending = filename[:-4].split('-')[-1]
      lemma_2 = lemma[:-1] + ending
      orth_2 = ET.SubElement(form, 'orth')
      orth_2.text = lemma_2

    entry = re.sub(r'<kz>`(.*?)`</kz>', '', entry).strip()

    ######
    # RE #
    ######

    rel_list = re.findall(r'\+<kz>.*?</kz>\+', entry)
    if rel_list:
      rel = ET.Element('re')
      for r in rel_list[0].split(','):
        form_rel = ET.SubElement(rel, 'form')
        orth_rel = ET.SubElement(form_rel, 'orth')
        orth_rel.text = re.sub(r'\+<kz>(.*?)</kz>\+', r'\1', r.strip())
      root.append(rel)
      entry = re.sub(r'\+<kz>.*?</kz>\+', '', entry)

    ###################
    # INFLECTED FORMS #
    ###################

    # there needs to be a comma in there, otherwise it'll pick up
    # parentheticals in the citations
    inf_list = re.findall(r'\(<kz>[а-өА-Ө, ]+,[а-өА-Ө, ]+</kz>\)', entry)
    if inf_list:
      inf_list = re.sub(r'\(<kz>([а-өА-Ө, ]+?)</kz>\)', r'\1', inf_list[0])
      for inf in inf_list.split(','):
        form_inf = ET.Element('form', attrib={'type':'inflected'})
        orth_inf = ET.SubElement(form_inf, 'orth')
        orth_inf.text = re.sub(r'\(<kz>([а-өА-Ө, ]+?)</kz>\)', r'\1', inf.strip())
        root.append(form_inf)
      entry = re.sub(r'\(<kz>[а-өА-Ө, ]+?</kz>\)', '', entry)

    #######
    # POS #
    #######

    # all entries which have a POS will have it for sure in the
    # 2nd position and possibly the 3rd (in the case of, e.g. "vbl. n.")
    words = entry.split(' ')
    pos_text = ''
    cutoff = 0
    if '.' in words[0]:
      pos_text += words[0][:-1]
      cutoff = 1
    if '.' in words[1]\
       and not re.match(r'[1-9]', words[1])\
       and not '(' in words[1]:
      pos_text += ' ' + words[1][:-1]
      cutoff = 2
    entry = ' '.join(words[cutoff:])
    pos.text = pos_text

    ########
    # ETYM #
    ########

    etym_list = re.findall(r'(\[.*?\])', entry)
    if etym_list:
      etym = ET.Element('etym')
      for et in etym_list:
        lang = ET.SubElement(etym, 'lang')
        lang.text = re.sub(r'[\[\]]', '', et)
      root.append(etym)
      entry = re.sub(r'(\[.*?\])', '', entry)

    ##########
    # SENSES #
    ##########

    entry = entry.strip()
    senses = re.findall(r'[0-9]+\. [^0-9]+', entry)
    if senses:
      for num, definition in enumerate(senses):
        sense(root, num + 1, definition)
    else:
      sense(root, 1, entry)

    # check if filename already exists, if so make into a superentry
    output_file = os.path.join('testing', lemma+'.xml')
    if duplicate_lemma:
      superEntry = ET.Element('superEntry')
      super_tree = ET.ElementTree(superEntry)
      existing = ET.parse(output_file)
      for e in existing.iter('entry'):
        superEntry.append(e)
      superEntry.append(root)
      super_tree.write(open(output_file, 'w'), encoding="unicode")
    else:
      tree.write(open(output_file, 'w'), encoding="unicode")
