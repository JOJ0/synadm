#!/usr/bin/env python
# Prerequisites: pip install -r scrape_docs_requirements.txt

import click
from bs4 import BeautifulSoup
import requests


@click.command()
@click.option(
    '--output', '-o', default='default',
    type=click.Choice(['default', 'rst', 'csv']), show_choices=True,
    help='''Output format "default" prints human readable on shell, "csv" is a
    two-column comma separated value format.''')
@click.argument('URL')
def scrape(output, url):
    '''Scrape one chapter of Admin API docs and spit out in various formats.

    URL is the address of the Synapse Admin API docs chapter. For example:
    https://element-hq.github.io/synapse/develop/admin_api/rooms.html'''
    chapter = url
    apidoc = requests.get(chapter).text
    soup = BeautifulSoup(apidoc, 'html.parser')

    elements = soup.find_all(
            ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a'],
    )

    for e in elements:
        if e.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            if output in ['default', 'rst']:
                print(f'{e.name}: {e.text}')
        if e.name == 'a':
            if e.parent.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                link = e['href']
                if output == 'default':
                    print(f'{e.text} {link}')
                if output in ['rst', 'csv']:
                    parts = chapter.split('/admin_api/')
                    fulllink = f'{parts[0]}/admin_api/{parts[1]}{link}'
                    if output == 'rst':
                        rst = f'`{e.text} <{fulllink}>`_'
                        print(rst)
                    # csv format also adds some spacing in front of links
                    if output == 'csv':
                        left_col = f'"  `{e.text} <{fulllink}>`_"'
                        print(f'{left_col},')
            # Final spacing only with these formats
            if output in ['default', 'rst']:
                print()

# print(soup.prettify())


if __name__ == '__main__':
    scrape()
