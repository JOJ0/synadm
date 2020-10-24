#!/usr/bin/env python3
import click
import requests
import requests.exceptions as reqerrors
import logging
from pathlib import Path
import os
import json
from pprint import pprint
from tabulate import tabulate

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

    def _get(self, urlpart):
        headers={'Accept': 'application/json' }
        tokenpart=f"access_token={self.token}"
        url="http://{}:{}/_synapse/admin/{}&{}".format(self.host, self.port,
              urlpart, tokenpart)
        log.debug('_get_synapse url: {}'.format(url))
        try:
            resp = requests.get(url, headers=headers, timeout=7)
            resp.raise_for_status()
            if resp.ok:
                _json = json.loads(resp.content)
                return _json
            else:
                log.warning("No valid response from Synapse. Returning None.")
                return None
        except reqerrors.HTTPError as errh:
            log.error("HTTPError: %s", errh)
            #if "Not found" in errh.response.text:
            #    log.warning("AcousticBrainz doesn't have this recording yet. Consider submitting it!")
            return None
        except reqerrors.ConnectionError as errc:
            log.error("ConnectionError: %s", errc)
            return None
        except reqerrors.Timeout as errt:
            log.error("Timeout: %s", errt)
            return None
        except reqerrors.RequestException as erre:
            log.error("RequestException: %s", erre)
            return None


    def user_list(self):
        ufrom = 0
        ulimit = 50
        udeactivated = 'false'
        urlpart = f'v2/users?from={ufrom}&limit={ulimit}&deactivated={udeactivated}'
        return self._get(urlpart)


def modify_usage_error(main_command):
    '''a method to append the help menu to an usage error
    :param main_command: top-level group or command object constructed by click wrapper
    '''
    from click._compat import get_text_stderr
    from click.utils import echo
    def show(self, file=None):
        import sys
        if file is None:
            file = get_text_stderr()
        color = None
        if self.ctx is not None:
            color = self.ctx.color
            echo(self.ctx.get_usage() + '\n', file=file, color=color)
        echo('Error: %s\n' % self.format_message(), file=file, color=color)
        sys.argv = [sys.argv[0]]
        main_command()

    click.exceptions.UsageError.show = show



log = logger_init()

@click.group(invoke_without_command=False)
@click.option('--verbose', '-v', count=True, default=False,
      help="enable INFO or DEBUG logging on console")
@click.option('--raw', '-r', is_flag=True, default=False,
      help="print raw json data (no tables)")
@click.pass_context
def synadm(ctx, verbose, raw):
    if verbose == 1:
        log.handlers[0].setLevel(logging.INFO) # set cli handler to INFO,
    elif verbose > 1:
        log.handlers[0].setLevel(logging.DEBUG) # or to DEBUG level

@click.command()
@click.argument('user_task')
@click.argument('args', nargs=-1)
@click.pass_context
def user(ctx, user_task, args):
    """list, add, modify or deactivate/delete users
       and reset passwords.
    """
    if user_task == "list":
        synadm = Synapse_admin()
        users = synadm.user_list()
        if users == None:
            click.echo("Users could not be fetched.")
            raise SystemExit(1)
        if ctx.parent.params['raw']:
            pprint(users)
            #print("this is ctx dir: {}".format(dir(ctx.parent)))
            #print("this is ctx: {}".format(ctx.parent.params))
        else:
            click.echo(
                  "\nTotal users on homeserver (excluding deactivated): {}\n".format(
                  users['total']))
            if int(users['total']) != 0:
                headers_dict = {}
                for header in users['users'][0]:
                    headers_dict.update({header: header})
                tab_users = tabulate(users['users'], tablefmt="simple",
                      headers=headers_dict)
                click.echo(tab_users)

    elif user_task == "add":
        pass

    

@click.command()
@click.argument('room_task')
@click.argument('args', nargs=-1)
@click.pass_context
def room(ctx, room_task, args):
    """list rooms, modify their settings,... FIXME
    """
    pass

synadm.add_command(user)
synadm.add_command(room)
#print(dir(synadm))
modify_usage_error(synadm)

if __name__ == '__main__':
    synadm(obj={})
