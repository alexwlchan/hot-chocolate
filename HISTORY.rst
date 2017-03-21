Release History
===============

2.0.0 (2017-03-1)
-----------------

Here "2.0" is really a count of the number of websites I have using this tool,
rather than a reflection of quality.  Lots of new stuff added since 1.0.2,
but mostly untested and documented (note to self: fix that!).

1.0.2 (2017-02-26)
------------------

Two accessibility-related bugfixes, both found with `pa11y <https://github.com/pa11y/pa11y>`_:

-  Render heading links as an HTML ``<ul>`` list.
-  Only include ``<h1>`` tags for the title of a page if the title is
   non-empty.

1.0.1 (2017-02-22)
------------------

Bugfixes:

-  Issue a better warning when trying to run on old versions of Python.
-  Default SCSS and HTML files that are part of the package are actually
   installed when you run ``pip install``.
-  Posts with metadata but no content render an empty page rather than
   raise a ``ValueError``.
-  Sites without the (optional) ``site:subtitle`` setting no longer raise
   a ``RuntimeError`` when trying to build.

1.0.0 (2017-02-22)
------------------

-  First production release!
