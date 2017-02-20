# -*- encoding: utf-8

import collections
import os

import dateutil.parser as dp
import markdown

from .css import CSSProcessor
from .settings import SiteSettings
from .utils import chunks, lazy_copyfile, slugify
from .writers import CocoaEnvironment


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

    def __init__(self):
        self.path = os.path.abspath(os.curdir)
        self.out_path = '_output'
        self.settings = SiteSettings(self.path)

        self.posts = []
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
            self.write_html(post.out_path, html)

        for page in self.pages:
            html = template.render(site=self, article=page, title=page.title)
            self.write_html(page.out_path, html)

        self._build_index()
        self._build_tag_indices()
        self._copy_static_files()

    @classmethod
    def from_folder(cls, path):
        """
        Construct a ``Site`` instance from a folder on disk.
        """
        site = cls()
        for root, _, filenames in os.walk(os.path.join(site.path, 'posts')):
            for f in filenames:
                if os.path.splitext(f)[1].lower() in MARKDOWN_EXTENSIONS:
                    site.posts.append(Post.from_file(os.path.join(root, f)))

        for root, _, filenames in os.walk(os.path.join(site.path, 'pages')):
            for f in filenames:
                if os.path.splitext(f)[1].lower() in MARKDOWN_EXTENSIONS:
                    site.pages.append(Page.from_file(os.path.join(root, f)))

        return site

    def _build_index(self, posts=None, prefix=''):
        # TODO: Make this more generic
        # TODO: Make pagination size a setting
        template = self.env.get_template('index.html')

        if posts is None:
            posts = self.posts

        posts = sorted(posts, key=lambda x: x.date, reverse=True)
        for pageno, p in enumerate(chunks(posts, 5), start=1):
            html = template.render(site=self, articles=p)

            if pageno == 1:
                slug = '/%s/' % prefix
            else:
                if prefix:
                    slug = '/%s/%d' % (prefix, pageno)
                else:
                    slug = '/page/%d' % pageno
            self.write_html(slug, html)

    def _build_tag_indices(self):
        tags = collections.defaultdict(list)
        for p in self.posts:
            for t in p.tags:
                tags[t].append(p)
        for t, posts in tags.items():
            self._build_index(
                posts=posts,
                prefix='/tag/%s' % t)

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
        self.title = metadata.pop('title')
        self.slug = metadata.get('slug')

        try:
            self.tags = [t.strip() for t in metadata.pop('tags').split(',')]
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
    def out_path(self):
        return self.slug

    @classmethod
    def from_file(cls, path):
        """
        Construct an ``Article`` instance from a file on disk.
        """
        file_contents = open(path).read()

        # Metadata is separated from the rest of the content by an empty line.
        # TODO: Make this robust to trailing whitespace.
        metadata_str, content = file_contents.split('\n\n', 1)

        # TODO: Handle quoted strings?  Lists?
        metadata = {}
        for line in metadata_str.splitlines():
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()

        # TODO: Use Smartypants here
        return cls(
            content=markdown.markdown(content),
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
    def out_path(self):
        return self.date.strftime('%Y/%m/') + self.slug
