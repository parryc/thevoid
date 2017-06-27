import markdown
from bracket_table import BracketTable

if __name__ == '__main__':
  out = markdown.markdown('{hello}\na|1\nb\n{/}',extensions=[BracketTable()])
  print out