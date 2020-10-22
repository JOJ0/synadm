#!/usr/bin/env python
import click
import requests
import requests.exceptions as reqerrors
import logging
from pathlib import Path
import os
import json

def logger_init():
    synadmin_root = Path(os.path.dirname(os.path.abspath(__file__)))
    debug_log = synadmin_root / "debug.log"

    log = logging.getLogger('synadm')
    log.setLevel(logging.DEBUG) # level of logger itself
    f_handle = logging.FileHandler(debug_log, encoding='utf-8') # create file handler
    f_handle.setLevel(logging.DEBUG) # which logs even debug messages
    c_handle = logging.StreamHandler() # console handler with a higher log level
    c_handle.setLevel(logging.WARNING) # level of the console handler
    # create formatters and add it to the handlers
    f_form = logging.Formatter('%(asctime)s %(name)-8s %(levelname)-7s %(message)s',
             datefmt='%Y-%m-%d %H:%M:%S')
    c_form = logging.Formatter('%(levelname)-5s %(message)s')
    c_handle.setFormatter(c_form)
    f_handle.setFormatter(f_form)
    log.addHandler(c_handle) # add the handlers to logger
    log.addHandler(f_handle)
    return log

class Synapse_admin (object):
    def __init__(self):
        self.host = 'localhost'
        self.port = 8008
        self.user = 'admin'
        self.token = os.getenv("SYNTOKEN")

    def _get_synapse(self, urlpart):
        headers={'Accept': 'application/json' }
        url="https://{}:{}/_synapse/admin/{}".format(self.host, self.port, urlpart)
        log.debug('_get_synapse url: {}'.format(urlpart))
        try:
            resp = requests.get(url, headers=headers, timeout=7)
            resp.raise_for_status()
            if resp.ok:
                _json = json.loads(resp.content)
                return _json
            else:
                log.debug("No valid response from Synapse. Returning None.")
                return None
        except reqerrors.HTTPError as errh:
            log.debug("HTTPError: %s", errh)
            #if "Not found" in errh.response.text:
            #    log.warning("AcousticBrainz doesn't have this recording yet. Consider submitting it!")
        except reqerrors.ConnectionError as errc:
            log.error("ConnectionError: %s", errc)
        except reqerrors.Timeout as errt:
            log.error("Timeout: %s", errt)
        except reqerrors.RequestException as erre:
            log.error("RequestException: %s", erre)


    def user_list(self):
        ufrom = 0
        ulimit = 50
        udeactivated = False
        urlpart = f'v2/users?access_token={self.token}&from={ufrom}&limit={ulimit}&deactivated={udeactivated}' 
        return self._get_synapse(urlpart) 


log = logger_init()

@click.group(invoke_without_command=False)
@click.option('--debug/--no-debug', is_flag=True, default=False)
@click.pass_context
def synadm(ctx, debug):
    #click.echo('synadm command group')
    ctx.obj['DEBUG'] = debug
    click.echo('Debug logging is %s' % (ctx.obj['DEBUG'] and 'on' or 'off'))
    if debug == True:
        log.handlers[0].setLevel(logging.DEBUG) # adjust cli handler only

@click.command()
@click.argument('command')
@click.argument('args', nargs=-1)
@click.pass_context
def user(ctx, command, args):
    click.echo('User subcommand: {} {}'.format(command, args))
    if command == "list":
        synadm = Synapse_admin()
        users = synadm.user_list()
        click.echo(users) # FIXME pretty print - build a class around tabulate or similar
    elif command == "add":
        pass

    

@click.command()
def room():
    click.echo('Room subcomand')

synadm.add_command(user)
synadm.add_command(room)
#print(dir(synadm))

if __name__ == '__main__':
    synadm(obj={})