# -*- encoding: utf-8

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
