# -*- encoding: utf-8

# flake8: noqa

import collections
from datetime import date, datetime
import itertools
import os
import re
import sys

import dateutil.parser as dp
import htmlmin
from feedgenerator import Atom1Feed, get_tag_uri

from . import markdown
from .css import load_base_css, minimal_css_for_html, optimize_css
from .logging import info
from .settings import SiteSettings
from .readers import list_page_files, list_post_files
from .plugins import load_plugins
from .templates import build_environment
from .utils import Pagination, lazy_copyfile, slugify


# TODO: Make this a setting
PAGE_SIZE = 10


class _SiteSettingDescriptor:
    def __init__(self, section, option):
        self.section = section
        self.option = option

    def __get__(self, instance, type):
        return instance.settings.get(self.section, self.option)


class Site:
    """
    Holds the settings for an individual site.
    """

    name            = _SiteSettingDescriptor('site', 'name')
    url             = _SiteSettingDescriptor('site', 'url')
    header_links    = _SiteSettingDescriptor('site', 'header_links')
    language        = _SiteSettingDescriptor('site', 'language')
    subtitle        = _SiteSettingDescriptor('site', 'subtitle')
    search_enabled  = _SiteSettingDescriptor('site', 'search_enabled')
    author          = _SiteSettingDescriptor('site', 'author')
    author_email    = _SiteSettingDescriptor('site', 'author_email')
    description     = _SiteSettingDescriptor('site', 'description')

    def __init__(self):
        self.path = os.path.abspath(os.curdir)
        self.out_path = '_output'
        self.settings = SiteSettings(self.path)

        self.posts = []
        self._tagged_posts = collections.defaultdict(list)
        self.pages = []
        self.env = build_environment()

        self.base_css = optimize_css(load_base_css())

        # Mapping from URL slugs to rendered HTML.
        # TODO: Check we don't write the same slug more than once.
        self._prepared_html = {}

    def write(self):
        for slug, html_str in self._prepared_html.items():
            self.write_html(slug=slug, html_str=html_str)

    def write_html(self, slug, html_str):
        """
        Writes a string to a path in the output directory.

        This creates a directory with an ``index.html`` file, so you get
        pretty URLs without needing web server configuration.
        """
        slug = slug.lstrip('/')
        os.makedirs(os.path.join(self.out_path, slug), exist_ok=True)

        # Insert any CSS into the page.
        # TODO: Replace this with a proper parser for extracting the HTML.
        body_html = html_str.split('<body>')[1].split('</body>')[0]
        css = minimal_css_for_html(body_html=body_html, css=self.base_css)
        html_str = html_str.replace(
            '<!-- hc_css_include -->', f'<style>{css}</style>'
        )

        html_str = htmlmin.minify(html_str)

        with open(os.path.join(self.out_path, slug, 'index.html'), 'w') as f:
            f.write(html_str)

    def build(self):
        """
        Build the complete site and write it to the output folder.
        """
        self._prepare_posts()
        self._prepare_pages()
        self._prepare_index(posts=self.posts)

        self._build_feeds()
        self._build_tag_indices()
        self._copy_static_files()
        self._build_date_archives()
        self._build_archive()
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
            self._prepared_html[post.url] = html

    def _prepare_pages(self):
        """Prepare the HTML for pages."""
        page_template = self.env.get_template('page.html')
        for page in self.pages:
            html = page_template.render(
                site=self,
                metadata=page.metadata,
                content=page.content
            )
            self._prepared_html[page.url] = html

    @classmethod
    def from_folder(cls, path):
        """
        Construct a ``Site`` instance from a folder on disk.
        """
        load_plugins(os.path.join(os.path.abspath(path), 'plugins'))
        site = cls()
        for path in list_post_files(site.path):
            info('Reading post from file %s',
                path.replace(site.path, '').lstrip('/'))
            p = Post.from_file(path)
            for t in p.tags:
                site._tagged_posts[t].append(p)
            site.posts.append(p)

        for path in list_page_files(site.path):
            info(
                'Reading page from file %s',
                path.replace(site.path, '').lstrip('/'))
            site.pages.append(Page.from_file(path))

        return site

    def _build_feeds(self):
        feed_kwargs = {
            'title': self.name,
            'link': self.url + '/feeds/all.atom.xml',
            'description': self.description,
            'author_name': self.author,
            'author_email': self.author_email,
        }
        feed = Atom1Feed(**feed_kwargs)

        for post in reversed(self.posts):
            post_kwargs = {
                'title': post.title,
                'link': self.url + post.url,
                'pubdate': post.date,
                'content': post.content,
            }
            if post.link is not None:
                post_kwargs['link'] = post.link
            if 'summary' in post.metadata:
                post_kwargs['description'] = post.metadata['summary']
            else:
                post_kwargs['description'] = post_kwargs['content']
            post_kwargs['unique_id'] = get_tag_uri(post_kwargs['link'], post.date)

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

        feed_dir = os.path.join(self.out_path, 'feeds')
        os.makedirs(feed_dir, exist_ok=True)
        feed.write(
            open(os.path.join(feed_dir, 'all.atom.xml'), 'w'),
            encoding='utf-8')

    def _prepare_index(self, posts, prefix='', title=None):
        """Prepare the HTML for a set of index pages."""
        index_template = self.env.get_template('index.html')
        posts = sorted(posts, key=lambda x: x.date, reverse=True)

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

    def _build_index(self, posts=None, prefix='', title=None):
        self._prepare_index(posts=posts, prefix=prefix, title=title)

    def _build_date_archives(self):
        def get_month(p):
            return date(p.date.year, p.date.month, 1)
        for m, posts in itertools.groupby(self.posts, get_month):
            self._build_index(
                posts=posts,
                prefix='/%04d/%02d' % (m.year, m.month),
                title=m.strftime('Posts from %B %Y'))

    def _build_archive(self):
        template = self.env.get_template('archive.html')
        def get_year(p):
            return p.date.year
        html = template.render(
            site=self,
            article_groups=itertools.groupby(
                sorted(self.posts, key=lambda p: p.date, reverse=True),
                get_year),
            title='Archives'
        )
        self.write_html('/archives/', html)

    def _build_tag_indices(self):
        for t, posts in self._tagged_posts.items():
            self._build_index(
                posts=posts,
                prefix='/tag/%s' % t,
                title='Tagged with “%s”' % t)

    def _copy_static_files(self):
        for root, _, filenames in os.walk(os.path.join(self.path, 'static')):
            for f in filenames:
                if f.startswith('.'):
                    continue
                base = os.path.join(root, f).replace(
                    self.path + '/static/', '')
                lazy_copyfile(
                    src=os.path.join(self.path, 'static', base),
                    dst=os.path.join(self.out_path, base),
                )


class Article:
    """
    Holds information about an individual article (a page or a post).
    """
    def __init__(self, content, metadata, path):
        self.content = content
        self.metadata = metadata
        self.path = path

        # TODO: better error handling
        self.title = markdown.convert_markdown(metadata['title'])
        # [len('<p>'):-len('</p>')]
        self.slug = metadata.get('slug')

        try:
            self.tags = sorted([
                t.strip()
                for t in metadata.pop('tags').split(',')
                if t.strip()])
        except KeyError:
            self.tags = []

        self.metadata = metadata

    def __repr__(self):
        return '<%s path=%r>' % (type(self).__name__, self.path)

    @property
    def slug(self):
        if self._slug is None:
            self._slug = slugify(self.title)
        return self._slug

    @slug.setter
    def slug(self, value):
        self._slug = value

    @property
    def url(self):
        return self.slug

    @property
    def link(self):
        return self.metadata.get('link')

    @classmethod
    def from_file(cls, path):
        """
        Construct an ``Article`` instance from a file on disk.
        """
        file_contents = open(path).read()

        # Metadata is separated from the rest of the content by an empty line.
        # TODO: Make this robust to trailing whitespace.
        try:
            metadata_str, content = file_contents.split('\n\n', 1)
        except ValueError:
            metadata_str, content = file_contents.strip(), ''

        # TODO: Handle quoted strings?  Lists?
        metadata = {}
        for line in metadata_str.splitlines():
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()

        return cls(
            content=markdown.convert_markdown(content),
            metadata=metadata,
            path=path)


# Add some error checking that these have the correct fields

class Page(Article):
    """
    Holds information about an individual page.
    """
    type = 'page'


class Post(Article):
    """
    Holds information about an individual post.
    """
    type = 'post'

    def __init__(self, content, metadata, path):
        super().__init__(content, metadata, path)
        self.metadata['date'] = dp.parse(self.metadata['date'])

    @property
    def url(self):
        return self.date.strftime('%Y/%m/') + self.slug

    @property
    def date(self):
        return self.metadata['date']
