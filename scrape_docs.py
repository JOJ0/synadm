#!/usr/bin/env python
# Prerequisites: pip install -e '.[scrape_docs]'
# Usage: scrape_docs.py --help

import click
from bs4 import BeautifulSoup
import requests


@click.command()
@click.option(
    '--output', '-o', default='csv',
    type=click.Choice(['debug', 'rst', 'csv']), show_choices=True,
    help='''Output format "debug" prints headline level, headline text and the
    scraped link/anchor; "rst" gives a restructuredText formatted hyperlink
    including indentation according to headline levels. Spaces at the beginning
    of lines have a special meaning in rst documents, thus the hardcoded
    replacement marker "|indent|" is used; "csv" is a two-column comma
    separated value format that includes the results of "rst" as the left
    column's contents.''')
@click.argument('URL')
def scrape(output, url):
    '''Scrape one chapter of Admin API docs and spit out in various formats.

    URL is the address of the Synapse Admin API docs chapter. For example:
    https://element-hq.github.io/synapse/latest/admin_api/rooms.html

    The default output format is "csv", which gives a two column CSV table
    containing restructuredText formatted hyperlinks and a headline.
    '''
    def get_indentation_levels(heading_tags, heading_tag):
        """Returns how many indentation levels are required depending on the
        passed heading tag

        h1 is no indentation,
        h2 is one indentation level,
        h3 is two, and so on...
        """
        for h in heading_tags:
            if heading_tag == h:
                return int(heading_tag[-1]) - 1
        return 0

    chapter = url
    apidoc = requests.get(chapter).text
    soup = BeautifulSoup(apidoc, 'html.parser')

    any_heading_tag = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    elements = soup.find_all([*any_heading_tag, 'a'],)

    for e in elements:
        if e.name in any_heading_tag and output == 'debug':
            print(f'{e.name}: {e.text}')
        if e.name == 'a':
            if e.parent.name in any_heading_tag:
                link = e['href']
                if output == 'debug':
                    print(f'Element text:\t{e.text}\nLink/Anchor:\t{link}')
                    indent_count = get_indentation_levels(any_heading_tag,
                                                          e.parent.name)
                    print(f'Indentations:\t{indent_count}')
                if output in ['rst', 'csv']:
                    parts = chapter.split('/admin_api/')
                    fulllink = f'{parts[0]}/admin_api/{parts[1]}{link}'
                    indent_count = get_indentation_levels(any_heading_tag,
                                                          e.parent.name)
                    spacing = ''
                    for val in range(0, indent_count):
                        # '|indent| ' represents one indentation level
                        spacing += '|indent| '
                    rst = f'{spacing}`{e.text} <{fulllink}>`_'
                    if output == 'csv':
                        left_col = f'"{rst}"'
                        print(f'{left_col},')
                    elif output == 'rst':
                        print(rst)
            if output == 'debug':  # Final spacing only with debug format
                print()

# print(soup.prettify())


if __name__ == '__main__':
    scrape()
