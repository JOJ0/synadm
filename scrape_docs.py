#!/usr/bin/env python

from bs4 import BeautifulSoup
import requests
import re
import pprint as p


chapter = 'https://element-hq.github.io/synapse/develop/admin_api/rooms.html'
apidoc = requests.get(chapter).text
soup = BeautifulSoup(apidoc, 'html.parser')

elements = soup.find_all(
        ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a'],
)

#p.pprint(elements)
for e in elements:
    if e.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        print(f'HEADLINE {e.name}: {e.text}')
    if e.name == 'a':
        if e.parent.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            link = e['href']
            print(f'{e.text} {link}')
            print()

print()
print()
print()

#print(soup.prettify())
