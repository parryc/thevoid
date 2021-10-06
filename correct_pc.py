import sys
import os
import re

folder = os.path.join(os.getcwd(), "templates", "parryc")
print folder

for filename in reversed(os.listdir(folder)):
    if filename[0] == ".":
        continue
    raw = open(os.path.join(folder, filename), "rb")
    text = raw.read()
    # print text
    _m = re.search(r"title: (.+)", text)
    if _m:
        date = filename[0:10]
        print "* [%s // %s](%s)" % (date, _m.group(1), filename.replace(".md", ""))

# for filename in os.listdir(folder):
#   if filename[0] == '.':
#     continue
#   raw = open(os.path.join(folder,filename),'rb')
#   out = open(os.path.join(folder,filename+'_temp'),'wb')
#   text = raw.read()
#   # print text
#   _m = re.search(r'title: (.+)',text)
#   if _m:
#     title = '#' + _m.group(1)
#     # print title
#     _m = re.search(r'categories:\s*\n- (.+)\n(- (.+)\n)?(- (.+)\n)?(- (.+)\n)?',text)
#     if _m:
#       categories = _m.groups()
#       category_text = ''
#       for category in categories:
#         if category and '-' not in category:
#           category_text += '<tag>%s</tag> ' % category
#       # print category_text
#     date = filename[0:10]
#     # print date

#     final_text = '\n%s\n%s\\\\\ %s' % (title, category_text, date)
#     print final_text

#     text = re.sub('-->','-->'+final_text,text,count=1)
#     print >>out,text

# for filename in os.listdir(folder):
#   print filename
#   if '_temp' not in filename:
#     os.remove(os.path.join(folder,filename))
#   if '_temp' in filename:
#     os.rename(os.path.join(folder,filename),filename.replace('_temp',''))
