"""Access the persistent configuration information."""

import json
import os
import logging

class Config(object):
    __instance = None
    __config_path = os.path.expanduser('~/.config/throw/throw.json')
    __log = logging.getLogger(__name__ + '.Config')

    # Each configuration option is in one section and has some help text
    # associated with it and, optionally, a default option if it is optional
    __options = {
        'user': {
            'name': { 'help': 'Your full name to use when sending email' },
            'email': { 'help': 'The email address to use when sending email' },
        },
        'smtp': {
            'host': {
                'help': 'The hostname of a SMTP server to use to send mail' },
            'port': {
                'help': 'The port to connect the to SMTP server when sending mail',
                'default': 25 },
            'use_tls': {
                'help': 'Use TLS when connecting to the SMTP server',
                'default': False },
            'use_ssl': {
                'help': 'Use SSL when connecting to the SMTP server',
                'default': False },
            'username': { 
                'help': 'Authenticate to the SMTP server with this username',
                'default': None },
            'password': {
                'help': 'Authenticate to the SMTP server with this username',
                'default': None },
        },
    }

    # Implement the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls._instance = super(Config, cls).\
                __new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        # Attempt to load the config file
        try:
            self._config_dict = json.load(open(Config.__config_path, 'r'))
            Config.__log.info('Loaded configuration from %s' % (Config.__config_path,))
        except IOError:
            self._config_dict = { }
            Config.__log.info('Loaded blank configuration')

    def _sync(self):
        if not os.path.exists(os.path.dirname(Config.__config_path)):
            os.makedirs(os.path.dirname(Config.__config_path))
        fp = open(Config.__config_path, 'w')
        json.dump(self._config_dict, fp, indent=4)

    def exists(self, section, option):
        if section not in self._config_dict:
            return False
        if option not in self._config_dict[section]:
            return False
        return True
    
    def get_section(self, section):
        if section not in self._config_dict:
            if section in Config.__options:
                fallback_dict = { }
                for option in Config.__options[section]:
                    if 'default' in Config.__options[section][option]:
                        fallback_dict[option] = \
                            Config.__options[section][option]['default']
                return fallback_dict
            raise KeyError('No fallback found for configuration section "%s".' % (section,))

        return self._config_dict[section]

    def get(self, section, option):
        if self.exists(section, option):
            if option in self._config_dict[section]:
                return self._config_dict[section][option]

        # We need to use a fallback, silently ignore a KeyError
        # if there is no default value.
        try:
            return Config.__options[section][option]['default']
        except KeyError:
            pass

        # If we got here, there was no fallback to return
        raise KeyError('No fallback found for configuration option "%s.%s"' % (section, option))
    
    def set(self, section, option, value):
        if section not in self._config_dict:
            self._config_dict[section] = { }

        self._config_dict[section][option] = value
        self._sync()
