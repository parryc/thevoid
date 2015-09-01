import sys
import os
import re
folder = os.path.join(os.getcwd(),'templates','parryc')
print folder
for filename in os.listdir(folder):
  if filename[0] == '.':
    continue
  text = open(os.path.join(folder,filename),'r').read()
  # print text
  _m = re.search(r'title: (.+)',text)
  title = '#' + _m.group(1)
  print title
  _m = re.search(r'categories:\s*\n- (.+)\n(- (.+)\n)?(- (.+)\n)?(- (.+)\n)?',text)
  if _m:
    categories = _m.groups()
    category_text = ''
    for category in categories:
      if category and '-' not in category:
        category_text += '<tag>%s</tag> ' % category
    print category_text
  date = filename[0:10]
  print date