# -*- encoding: utf-8

import os

from jinja2 import Environment, PackageLoader, select_autoescape
import markdown


MARKDOWN_EXTENSIONS = ('.txt', '.md', '.mdown', '.markdown')


class Site:
    """
    Holds the settings for an individual site.
    """
    def __init__(self, language=None):
        self.language = language or 'en'
        self.posts = []

    @classmethod
    def from_folder(cls, path):
        """
        Construct a ``Site`` instance from a folder on disk.
        """
        s = cls()
        for root, _, filenames in os.walk(os.path.join(path, 'posts')):
            for f in filenames:
                if os.path.splitext(f)[1].lower() in MARKDOWN_EXTENSIONS:
                    s.posts.append(Article.from_file(os.path.join(root, f)))
        return s


class Article:
    """
    Holds information about an individual article (a page or a post).
    """
    def __init__(self, content, path=None):
        self.content = content
        self.path=path

    def __repr__(self):
        return '<%s path=%r>' % (type(self).__name__, self.path)

    @classmethod
    def from_file(cls, path):
        """
        Construct an ``Article`` instance from a file on disk.
        """
        return cls(
            content=markdown.markdown(open(path).read()),
            path=path)


def main():
    print('Welcome to Cacao!')
    env = Environment(
        loader=PackageLoader('cacao', 'templates'),
        autoescape=select_autoescape(['html'])
    )
    site = Site.from_folder('content')
    for i, post in enumerate(site.posts):
        template = env.get_template('article.html')
        with open('example_%d.html' % i, 'w') as f:
            f.write(template.render(site=site, article=post))
