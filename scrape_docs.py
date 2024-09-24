#!/usr/bin/env python
# Prerequisites: pip install -e .[scrape_docs]

import click
from bs4 import BeautifulSoup
import requests


@click.command()
@click.option(
    '--output', '-o', default='csv',
    type=click.Choice(['debug', 'rst', 'csv']), show_choices=True,
    help='''Output format "debug" prints headline level, headline text and the
    scraped link/anchor; "rst" gives a restructuredText formatted hyperlink
    including space-indentation according to headline levels; "csv" is a
    two-column comma separated value format that includes the results of "rst"
    as the left column's contents. Additionally "csv" adds a restructuredText
    formatted headline above the table''')
@click.argument('URL')
def scrape(output, url):
    '''Scrape one chapter of Admin API docs and spit out in various formats.

    URL is the address of the Synapse Admin API docs chapter. For example:
    https://element-hq.github.io/synapse/latest/admin_api/rooms.html

    The default output format is "csv", which gives a two column CSV table
    containing restructuredText formatted hyperlinks and a headline.
    '''
    chapter = url
    apidoc = requests.get(chapter).text
    soup = BeautifulSoup(apidoc, 'html.parser')

    any_heading_tag = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    elements = soup.find_all([*any_heading_tag, 'a'],)

    if output == 'csv':
        print('Change this headline as required')
        print('================================\n')
        print('"Synapse Admin API","synadm command(s)"')

    for e in elements:
        if e.name in any_heading_tag and output == 'debug':
            print(f'{e.name}: {e.text}')
        if e.name == 'a':
            if e.parent.name in any_heading_tag:
                link = e['href']
                if output == 'debug':
                    print(f'Element text:\t{e.text}\nLink/Anchor:\t{link}')
                if output in ['rst', 'csv']:
                    parts = chapter.split('/admin_api/')
                    fulllink = f'{parts[0]}/admin_api/{parts[1]}{link}'
                    spacing = ''
                    for h in any_heading_tag:
                        if e.parent.name == h:
                            # h1 is no spacing (decrease by 1),
                            # h2 is 2 spaces, h3 is 4....
                            spacing_count = int(e.parent.name[-1]) - 1
                            for val in range(0, spacing_count * 2):
                                spacing += ' '
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
