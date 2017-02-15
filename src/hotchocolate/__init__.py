# -*- encoding: utf-8

import collections
import os
import tempfile

import dateutil.parser as dp
from jinja2 import (
    Environment, FileSystemLoader, PackageLoader, select_autoescape)
import markdown

from .utils import chunks, lazy_copyfile, slugify


MARKDOWN_EXTENSIONS = ('.txt', '.md', '.mdown', '.markdown')


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
            for tmpl in os.listdir(os.path.join(path, 'templates')):
                if os.path.basename(tmpl).startswith('.'):
                    continue
                os.link(
                    src=os.path.abspath(tmpl),
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
            print(self.workdir)
            for tmpl in os.listdir(package_dir):
                name = os.path.basename(tmpl)
                if name.startswith('.'):
                    continue
                try:
                    os.link(
                        src=os.path.abspath(tmpl),
                        dst=os.path.join(self.workdir, name)
                    )
                except FileExistsError:
                    pass
            self.env = Environment(
                loader=FileSystemLoader(self.workdir),
                autoescape=select_autoescape(['html'])
            )

    def get_template(self, *args, **kwargs):
        return self.env.get_template(*args, **kwargs)


def write_html(output_dir, slug, string):
    """
    Writes a string to a path in the output directory.

    This creates a directory with an ``index.html`` file, so you get
    pretty URLs without needing web server configuration.
    """
    slug = slug.lstrip('/')
    os.makedirs(os.path.join(output_dir, slug), exist_ok=True)
    with open(os.path.join(output_dir, slug, 'index.html'), 'w') as f:
        f.write(string)


class Site:
    """
    Holds the settings for an individual site.
    """
    def __init__(self, path, out_path, language=None):
        self.path = path
        self.out_path = out_path
        self.language = language or 'en'
        self.posts = []
        self.pages = []
        self.env = CocoaEnvironment(path)

    def build(self):
        """
        Build the complete site and write it to the output folder.
        """
        template = self.env.get_template('article.html')
        # TODO: Spot if we've written multiple items with the same slug
        for post in self.posts:
            html = template.render(site=self, article=post)
            write_html(self.out_path, post.out_path, html)

        for page in self.pages:
            html = template.render(site=self, article=page)
            write_html(self.out_path, page.out_path, html)

        self._build_index()
        self._build_tag_indices()
        self._copy_static_files()

    @classmethod
    def from_folder(cls, path):
        """
        Construct a ``Site`` instance from a folder on disk.
        """
        s = cls(path=path, out_path='output')
        for root, _, filenames in os.walk(os.path.join(path, 'posts')):
            for f in filenames:
                if os.path.splitext(f)[1].lower() in MARKDOWN_EXTENSIONS:
                    s.posts.append(Post.from_file(os.path.join(root, f)))

        for root, _, filenames in os.walk(os.path.join(path, 'pages')):
            for f in filenames:
                if os.path.splitext(f)[1].lower() in MARKDOWN_EXTENSIONS:
                    s.pages.append(Page.from_file(os.path.join(root, f)))

        return s

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
            write_html(self.out_path, slug, html)

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

        return cls(
            content=markdown.markdown(content),
            metadata=metadata,
            path=path)


class Page(Article):
    """
    Holds information about an individual page.
    """
    pass


class Post(Article):
    """
    Holds information about an individual post.
    """
    def __init__(self, content, metadata, path):
        # TODO: Error handling
        self.date = dp.parse(metadata.pop('date'))
        super().__init__(content, metadata, path)

    @property
    def out_path(self):
        return self.date.strftime('%Y/%m/') + self.slug
