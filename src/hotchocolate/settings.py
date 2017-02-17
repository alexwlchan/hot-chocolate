# -*- encoding: utf-8

from configparser import ConfigParser, NoOptionError, NoSectionError
import collections
import os


DEFAULT_SETTINGS = {
    'site': {
        'name': 'My Great Site',
        'header_links': {},
        'language': 'en',
    },
}


class SiteSettings:

    def __init__(self, path):
        self.config = ConfigParser()
        self.config.read(os.path.join(path, 'config.ini'))

    def get(self, section, option):
        try:
            value = self.config.get(section, option)
        except (NoOptionError, NoSectionError):
            try:
                value = DEFAULT_SETTINGS[section][option]
            except KeyError:
                raise RuntimeError('No such setting %s:%s' % (section, option))

        if (section, option) == ('site', 'header_links'):
            result = collections.OrderedDict()
            for line in value.strip().splitlines():
                url, description = line.strip('-').strip().split(' ', 1)
                result[url] = description
            value = result

        return value
