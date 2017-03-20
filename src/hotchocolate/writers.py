# -*- encoding: utf-8

import os
import tempfile

from jinja2 import (
    Environment, FileSystemLoader, PackageLoader, select_autoescape)

from .utils import chunks


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

            yield {
                'slug': slug,
                'articles': posts,
                'next': next_,
                'prev': prev_,
            }


def locale_date(date):
    """
    Render a date in the current locale date.
    """
    # TODO: Make this configurable
    return date.strftime('%-d %B %Y')


class CocoaEnvironment(object):
    """
    Wrapper for ``jinja2.Environment`` that allows the user to override
    templates with files in a local directory.
    """
    def __init__(self, path):
        self.workdir = tempfile.mkdtemp(prefix='cocoa_templates_')

        # Drop in any templates from the local directory.  Because we need
        # to cope with relative imports and the like, we just copy them
        # all to a temporary directory and work from there.
        try:
            os.makedirs(self.workdir, exist_ok=True)
            tmpl_path = os.path.join(path, 'templates')
            for tmpl in os.listdir(tmpl_path):
                if os.path.basename(tmpl).startswith('.'):
                    continue
                os.link(
                    src=os.path.abspath(os.path.join(tmpl_path, tmpl)),
                    dst=os.path.join(self.workdir, os.path.basename(tmpl))
                )
            if os.listdir(self.workdir) == []:
                raise FileNotFoundError('No custom templates')

        # If there aren't any custom templates, just use them directly
        # from the package itself.
        except FileNotFoundError:
            self.env = Environment(
                loader=PackageLoader('hotchocolate', 'templates'),
                autoescape=select_autoescape(['html'])
            )

        # Otherwise, copy across the templates from the package
        # directory and then use a FileSystemLoader.
        else:
            package_dir = os.path.join(os.path.dirname(__file__), 'templates')
            for tmpl in os.listdir(package_dir):
                name = os.path.basename(tmpl)
                if name.startswith('.'):
                    continue
                try:
                    os.link(
                        src=os.path.abspath(os.path.join(package_dir, tmpl)),
                        dst=os.path.join(self.workdir, name)
                    )
                except FileExistsError:
                    pass
            self.env = Environment(
                loader=FileSystemLoader(self.workdir),
                autoescape=select_autoescape(['html'])
            )

        self.env.filters['locale_date'] = locale_date

    def get_template(self, path):
        return self.env.get_template(path)
