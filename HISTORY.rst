Release History
===============

1.1-dev
-------

Features:

- Minify HTML upon export.

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
