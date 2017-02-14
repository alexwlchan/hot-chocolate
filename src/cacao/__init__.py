# -*- encoding: utf-8

from jinja2 import Environment, PackageLoader, select_autoescape
import markdown


class Site:
    """
    Holds the settings for an individual site.
    """
    def __init__(self, language=None):
        self.language = language or 'en'


class Article:
    """
    Holds information about an individual article (a page or a post).
    """
    def __init__(self, content, path=None):
        self.content = content
        self.path=path

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
    site = Site()
    template = env.get_template('article.html')
    article = Article.from_file('example.md')
    with open('example.html', 'w') as f:
        f.write(template.render(site=site, article=article))
