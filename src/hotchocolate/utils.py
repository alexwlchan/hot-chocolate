# -*- encoding: utf-8

import filecmp
import os
import re
import shutil

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


def lazy_copyfile(src, dst):
    """
    Copy a file from ``src`` to ``dst``, but only if the files are different.

    Avoids thrashing the disk unnecessarily on repeated site builds.
    """
    assert os.path.exists(src)
    if os.path.exists(dst):
        if os.path.getmtime(dst) >= os.path.getmtime(src):
            return
        elif filecmp.cmp(src, dst):
            return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)
