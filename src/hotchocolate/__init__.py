# -*- encoding: utf-8

# flake8: noqa

import collections
import concurrent.futures
from datetime import date, datetime
import itertools
import os
import re
import sys

import dateutil.parser as dp
import htmlmin
from feedgenerator import Atom1Feed, get_tag_uri

from . import logging, markdown, plugins
from .css import load_base_css, minimal_css_for_html, optimize_css
from .logging import info
from .readers import list_page_files, list_post_files
from .site import NewSite
from .settings import load_settings, validate_settings
from .templates import build_environment
from .utils import Pagination, lazy_copyfile, slugify


# TODO: Make this a setting
PAGE_SIZE = 10


class Site(NewSite):
    """Represents a single site."""

    def __init__(self, settings):
        self.path = os.path.abspath(os.curdir)
        self.settings = settings
        validate_settings(self.settings)

        self.posts = []
        self.pages = []
        self.env = build_environment()

        # Mapping from URL slugs to rendered HTML.
        # TODO: Check we don't write the same slug more than once.
        self._prepared_html = {}

    def write(self):
        """Write all the prepared HTML to files on disk."""
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.write_html, slug, html_str): slug
                for slug, html_str in self._prepared_html.items()
            }
            for future in concurrent.futures.as_completed(futures):
                logging.info('Written HTML for %s', futures[future])

    def write_html(self, slug, html_str):
        """
        Writes a string to a path in the output directory.

        This creates a directory with an ``index.html`` file, so you get
        pretty URLs without needing web server configuration.
        """
        slug = slug.lstrip('/')
        os.makedirs(os.path.join(site.OUTPUT_DIR, slug), exist_ok=True)

        with open(os.path.join(site.OUTPUT_DIR, slug, 'index.html'), 'w') as f:
            f.write(html_str)

    def build(self):
        """
        Build the complete site and write it to the output folder.
        """
        self.posts = sorted(self.posts, key=lambda x: x.metadata['date'], reverse=True)

        self._prepare_posts()
        self._prepare_pages()
        self._prepare_index(posts=self.posts)
        self._prepare_date_index()
        self._prepare_archive()
        self._prepare_tag_index()

        css_string = optimize_css(load_base_css())
        self.add_css_to_html(css_string=css_string)

        self.optimise_html()

        self._build_feeds()
        self._copy_static_files()
        self.write()

    def _prepare_posts(self):
        """Prepare the HTML for posts."""
        post_template = self.env.get_template('post.html')
        for post in self.posts:
            html = post_template.render(
                site=self,
                metadata=post.metadata,
                content=post.content
            )
            self._prepared_html[post.metadata['url']] = html

    def _prepare_pages(self):
        """Prepare the HTML for pages."""
        page_template = self.env.get_template('page.html')
        for page in self.pages:
            html = page_template.render(
                site=self,
                metadata=page.metadata,
                content=page.content
            )
            self._prepared_html[page.metadata['url']] = html

    def _prepare_index(self, posts, prefix='', title=None):
        """Prepare the HTML for a set of index pages."""
        index_template = self.env.get_template('index.html')
        posts = sorted(posts, key=lambda x: x.metadata['date'], reverse=True)

        pagination = Pagination(
            posts=posts, page_size=PAGE_SIZE, prefix=prefix
        )

        for pageset in pagination:
            html = index_template.render(
                site=self,
                posts=pageset.posts,
                title=title,
                pageset=pageset
            )
            self._prepared_html[pageset.slug] = html

    def _prepare_date_index(self):
        """Prepare the HTML for the date-based index."""
        def get_month(p):
            return date(p.metadata['date'].year, p.metadata['date'].month, 1)

        for m, posts in itertools.groupby(self.posts, get_month):
            self._prepare_index(
                posts=posts,
                prefix='/%04d/%02d' % (m.year, m.month),
                title=m.strftime('Posts from %B %Y')
            )

    def _prepare_archive(self):
        archive_template = self.env.get_template('archive.html')

        def get_year(p):
            return p.metadata['date'].year

        html = archive_template.render(
            site=self,
            post_groups=itertools.groupby(self.posts, get_year),
            title='Archives'
        )
        self._prepared_html['/archives/'] = html

    def _prepare_tag_index(self):
        """Prepare the HTML for the tag-based index."""
        tags = collections.defaultdict(list)
        for p in self.posts:
            for t in p.metadata['tags']:
                tags[t].append(p)

        for t, posts in tags.items():
            self._prepare_index(
                posts=posts,
                prefix='/tag/%s' % t,
                title='Tagged with “%s”' % t
            )

    @classmethod
    def from_folder(cls, path):
        """Construct a ``Site`` instance from a folder on disk."""
        site = cls(settings=load_settings(path))
        for path in list_post_files(site.path):
            info('Reading post from file %s',
                path.replace(site.path, '').lstrip('/'))
            site.posts.append(Post.from_file(path))

        for path in list_page_files(site.path):
            info(
                'Reading page from file %s',
                path.replace(site.path, '').lstrip('/'))
            site.pages.append(Page.from_file(path))

        return site

    def _build_feeds(self):
        feed_kwargs = {
            'title': self.settings['name'],
            'link': self.settings['url'] + '/feeds/all.atom.xml',
            'description': self.settings['description'],
            'author_name': self.settings['author'],
            'author_email': self.settings['author_email'],
        }
        feed = Atom1Feed(**feed_kwargs)

        for post in reversed(self.posts):
            post_kwargs = {
                'title': post.metadata['title'],
                'link': self.settings['url'] + post.metadata['url'],
                'pubdate': post.metadata['date'],
                'content': post.content,
            }
            if post.metadata.get('link') is not None:
                post_kwargs['link'] = post.metadata.get('link')
            if 'summary' in post.metadata:
                post_kwargs['description'] = post.metadata['summary']
            else:
                post_kwargs['description'] = post_kwargs['content']
            post_kwargs['unique_id'] = get_tag_uri(post_kwargs['link'], post.metadata['date'])

            if '<blockquote class="update">' in post.content:
                update_strings = re.findall(
                    r'Update, [0-9]+ [A-Z][a-z]+ [0-9]{4}', post.content
                )
                updated = max([
                    datetime.strptime(u, 'Update, %d %B %Y')
                    for u in update_strings
                ])
                post_kwargs['updateddate'] = updated

            feed.add_item(**post_kwargs)

        feed_dir = os.path.join(site.OUTPUT_DIR, 'feeds')
        os.makedirs(feed_dir, exist_ok=True)
        feed.write(
            open(os.path.join(feed_dir, 'all.atom.xml'), 'w'),
            encoding='utf-8')

    def _copy_static_files(self):
        for root, _, filenames in os.walk(os.path.join(self.path, 'static')):
            for f in filenames:
                if f.startswith('.'):
                    continue
                base = os.path.join(root, f).replace(
                    self.path + '/static/', '')
                lazy_copyfile(
                    src=os.path.join(self.path, 'static', base),
                    dst=os.path.join(site.OUTPUT_DIR, base),
                )


class Article:
    """
    Holds information about an individual article (a page or a post).
    """
    def __init__(self, content, metadata, path):
        self.content = content
        self.metadata = metadata
        self.path = path

        if 'slug' not in self.metadata:
            self.metadata['slug'] = slugify(self.metadata['title'])

        self.metadata['url'] = self.metadata['slug']

        try:
            self.metadata['tags'] = sorted([
                t.strip()
                for t in self.metadata.get('tags', '').split(',')
                if t.strip()])
        except KeyError:
            pass

        self.metadata = metadata

    def __repr__(self):
        return '<%s path=%r>' % (type(self).__name__, self.path)

    @classmethod
    def from_string(cls, path, file_contents):
        """Construct an instance from a string read from a file."""
        html, metadata = markdown.convert_markdown(
            file_contents,
            extra_extensions=plugins.load_markdown_extensions()
        )

        metadata = {k: v[0] for k, v in metadata.items()}

        return cls(
            content=html,
            metadata=metadata,
            path=path)

    @classmethod
    def from_file(cls, path):
        """Construct an ``Article`` instance from a file on disk."""
        file_contents = open(path).read()
        return cls.from_string(path=path, file_contents=file_contents)


# Add some error checking that these have the correct fields

class Page(Article):
    """Holds information about an individual page."""
    pass


class Post(Article):
    """Holds information about an individual post."""
    def __init__(self, content, metadata, path):
        super().__init__(content, metadata, path)
        self.metadata['date'] = dp.parse(self.metadata['date'])
        self.metadata['url'] = self.metadata['date'].strftime('%Y/%m/') + self.metadata['slug']
