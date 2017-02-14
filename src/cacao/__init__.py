# -*- encoding: utf-8

import os

import dateutil.parser as dp
from jinja2 import Environment, PackageLoader, select_autoescape
import markdown

from .utils import chunks, slugify


MARKDOWN_EXTENSIONS = ('.txt', '.md', '.mdown', '.markdown')


ENV = Environment(
    loader=PackageLoader('cacao', 'templates'),
    autoescape=select_autoescape(['html'])
)


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
    def __init__(self, language=None):
        self.language = language or 'en'
        self.posts = []
        self.pages = []

    def build(self, output_dir):
        """
        Build the complete site and write it to the output folder.
        """
        template = ENV.get_template('article.html')
        # TODO: Spot if we've written multiple items with the same slug
        for post in self.posts:
            html = template.render(site=self, article=post)
            write_html(output_dir, post.output_path, html)

        for page in self.pages:
            html = template.render(site=self, article=page)
            write_html(output_dir, page.output_path, html)

        self._build_index(output_dir)

    @classmethod
    def from_folder(cls, path):
        """
        Construct a ``Site`` instance from a folder on disk.
        """
        s = cls()
        for root, _, filenames in os.walk(os.path.join(path, 'posts')):
            for f in filenames:
                if os.path.splitext(f)[1].lower() in MARKDOWN_EXTENSIONS:
                    s.posts.append(Post.from_file(os.path.join(root, f)))

        for root, _, filenames in os.walk(os.path.join(path, 'pages')):
            for f in filenames:
                if os.path.splitext(f)[1].lower() in MARKDOWN_EXTENSIONS:
                    s.pages.append(Page.from_file(os.path.join(root, f)))

        return s

    def _build_index(self, output_dir):
        # TODO: Make this more generic
        # TODO: Make pagination size a setting
        template = ENV.get_template('index.html')
        posts = sorted(self.posts, key=lambda x: x.date, reverse=True)
        for i, p in enumerate(chunks(posts, 10), start=1):
            html = template.render(site=self, articles=p)
            if i == 1:
                write_html(output_dir, '/', html)
            else:
                write_html(output_dir, '/page/%d' % i, html)


class Article:
    """
    Holds information about an individual article (a page or a post).
    """
    def __init__(self, content, metadata, path):
        self.content = content
        self.metadata = metadata
        self.path=path

        # TODO: better error handling
        self.title = metadata.pop('title')
        self.slug = metadata.get('slug')
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
    def output_path(self):
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
    def output_path(self):
        return self.date.strftime('%Y/%m/') + self.slug


def main():
    print('Welcome to Cacao!')
    env = Environment(
        loader=PackageLoader('cacao', 'templates'),
        autoescape=select_autoescape(['html'])
    )
    site = Site.from_folder('content')
    site.build('output')
