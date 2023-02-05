import re

pattern = re.compile(r'(<img src)|!\[.*?\]\(.*?\)|^\n$')

print(pattern.search("h\n"))