# -*- encoding: utf-8

import re

from unidecode import unidecode


def slugify(u):
    """Convert Unicode string into blog slug."""
    # http://www.leancrew.com/all-this/2014/10/asciifying/
    u = re.sub(u'[–—/:;,.]', '-', u)   # replace separating punctuation
    a = unidecode(u).lower()           # best ASCII substitutions, lowercased
    a = re.sub(r'[^a-z0-9 -]', '', a)  # delete any other characters
    a = a.replace(' ', '-')            # spaces to hyphens
    a = re.sub(r'-+', '-', a)          # condense repeated hyphens
    return a


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    # http://stackoverflow.com/a/312464/1558022
    # Note: this only works if we know hte length of ``l``.
    for i in range(0, len(l), n):
        yield l[i:i + n]
