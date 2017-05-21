# -*- encoding: utf-8

import collections
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


Pageset = collections.namedtuple('Pageset', ['slug', 'posts', 'next', 'prev'])


class Pagination:
    """
    Provides pagination for a series of posts.

    Given a series of posts, the page size and the URL prefix
    (i.e. what's the URL slug for this series of posts), you can iterate
    over this object to get the collection of posts, slug and next/prev links
    for these posts.
    """
    def __init__(self, posts, page_size, prefix):
        self.posts = posts
        self.size = page_size
        self.prefix = prefix.strip('/')

    def __iter__(self):
        for pageno, posts in enumerate(chunks(self.posts, self.size), start=1):
            if pageno == 1:
                if self.prefix:
                    slug = '/%s/' % self.prefix
                else:
                    slug = '/'
                prev_ = None
            else:
                prefix = self.prefix or 'page'
                prev_ = slug
                slug = '/%s/%d/' % (prefix, pageno)

            if self.size * pageno >= len(self.posts):
                next_ = None
            else:
                prefix = self.prefix or 'page'
                next_ = '/%s/%d/' % (prefix, pageno + 1)

            yield Pageset(slug, posts, next_, prev_)
