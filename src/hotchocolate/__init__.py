# -*- encoding: utf-8

import collections
import os
import sys

import dateutil.parser as dp
import htmlmin

if sys.version_info < (3, 4):  # noqa
    raise ImportError(
        'Hot Chocolate is not supported on Python versions before 3.4'
    )

from .css import CSSProcessor
from .logging import info
from .markdown import Markdown
from .settings import SiteSettings
from .plugins import load_plugins
from .utils import lazy_copyfile, slugify
from .writers import CocoaEnvironment, Pagination


# TODO: Make this a setting
PAGE_SIZE = 10

MARKDOWN_EXTENSIONS = ('.txt', '.md', '.mdown', '.markdown')


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

    name = _SiteSettingDescriptor('site', 'name')
    header_links = _SiteSettingDescriptor('site', 'header_links')
    language = _SiteSettingDescriptor('site', 'language')
    subtitle = _SiteSettingDescriptor('site', 'subtitle')
    search_enabled = _SiteSettingDescriptor('site', 'search_enabled')

    def __init__(self):
        self.path = os.path.abspath(os.curdir)
        self.out_path = '_output'
        self.settings = SiteSettings(self.path)

        self.posts = []
        self._tagged_posts = collections.defaultdict(list)
        self.pages = []
        self.env = CocoaEnvironment(self.path)
        self.css_proc = CSSProcessor(self.path)

    def write_html(self, slug, html_str):
        """
        Writes a string to a path in the output directory.

        This creates a directory with an ``index.html`` file, so you get
        pretty URLs without needing web server configuration.
        """
        slug = slug.lstrip('/')
        os.makedirs(os.path.join(self.out_path, slug), exist_ok=True)

        html_str = self.css_proc.insert_css_for_page(html_str)
        html_str = htmlmin.minify(html_str)

        with open(os.path.join(self.out_path, slug, 'index.html'), 'w') as f:
            f.write(html_str)

    def build(self):
        """
        Build the complete site and write it to the output folder.
        """
        template = self.env.get_template('article.html')
        # TODO: Spot if we've written multiple items with the same slug
        for post in self.posts:
            html = template.render(site=self, article=post, title=post.title)
            self.write_html(post.url, html)

        for page in self.pages:
            html = template.render(site=self, article=page, title=page.title)
            self.write_html(page.url, html)

        self._build_index()
        self._build_tag_indices()
        self._copy_static_files()

    @classmethod
    def from_folder(cls, path):
        """
        Construct a ``Site`` instance from a folder on disk.
        """
        load_plugins(os.path.join(os.path.abspath(path), 'plugins'))
        site = cls()
        for root, _, filenames in os.walk(os.path.join(site.path, 'posts')):
            for f in filenames:
                if os.path.splitext(f)[1].lower() in MARKDOWN_EXTENSIONS:
                    pth = os.path.join(root, f)
                    info(
                        'Reading post from file %s',
                        pth.replace(site.path, '').lstrip('/'))
                    p = Post.from_file(pth)
                    for t in p.tags:
                        site._tagged_posts[t].append(p)
                    site.posts.append(p)

        for root, _, filenames in os.walk(os.path.join(site.path, 'pages')):
            for f in filenames:
                if os.path.splitext(f)[1].lower() in MARKDOWN_EXTENSIONS:
                    pth = os.path.join(root, f)
                    info(
                        'Reading page from file %s',
                        pth.replace(site.path, '').lstrip('/'))
                    site.pages.append(Page.from_file(pth))

        return site

    def _build_index(self, posts=None, prefix='', title=None):
        # TODO: Make this more generic
        # TODO: Make pagination size a setting
        template = self.env.get_template('index.html')

        if posts is None:
            posts = self.posts
        posts = sorted(posts, key=lambda x: x.date, reverse=True)

        pagination = Pagination(
            posts=posts, page_size=PAGE_SIZE, prefix=prefix
        )

        for pageset in pagination:
            html = template.render(
                site=self,
                articles=pageset['articles'],
                title=title,
                pageset=pageset
            )
            self.write_html(pageset['slug'], html)

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
    markdown = Markdown()

    def __init__(self, content, metadata, path):
        self.content = content
        self.metadata = metadata
        self.path = path

        # TODO: better error handling
        self.title = metadata.pop('title')
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
            content=cls.markdown.convert(content),
            metadata=metadata,
            path=path)


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
        # TODO: Error handling
        self.date = dp.parse(metadata.pop('date'))
        super().__init__(content, metadata, path)

    @property
    def url(self):
        return self.date.strftime('%Y/%m/') + self.slug
