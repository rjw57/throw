import json
import os

class Config(object):
    _instance = None
    _config_path = os.path.expanduser('~/.config/throw/throw.json')

    # Implement the singleton pattern
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).\
                __new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        # Attempt to load the config file
        try:
            self._config_dict = json.load(open(Config._config_path, 'r'))
        except IOError:
            self._config_dict = { }

    def _sync(self):
        try:
            fp = open(Config._config_path, 'w')
        except IOError:
            os.makedirs(os.path.dirname(Config._config_path))
            fp = open(Config._config_path, 'w')
        json.dump(self._config_dict, fp, indent=4)

    def exists(self, section, option):
        if section not in self._config_dict:
            return False
        if option not in self._config_dict[section]:
            return False
        return True
    
    def get(self, section, option, fallback=None):
        if not self.exists(section, option):
            return fallback
        return self._config_dict[section][option]
    
    def set(self, section, option, value):
        if section not in self._config_dict:
            self._config_dict[section] = { }

        self._config_dict[section][option] = value
        self._sync()
