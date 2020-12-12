def create_config_dir():
    home = Path(os.getenv('HOME'))
    Path.mkdir(home / '.config', exist_ok=True)
    synadm_config = home / '.config'
    return synadm_config

def create_data_dir():
    home = Path(os.getenv('HOME'))
    Path.mkdir(home / '.local' / 'share' / 'synadm', parents=True, exist_ok=True)
    synadm_data = home / '.local' / 'share' / 'synadm'
    return synadm_data

def logger_init():
    synadm_data = create_data_dir()
    debug_log = synadm_data / "debug.log"

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
