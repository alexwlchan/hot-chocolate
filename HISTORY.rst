Release History
===============

3.0.0 (2017-05-21)
------------------

A fairly significant rewrite of the internals:

-  Now only supporting Python 3.6.
-  Settings are now defined in TOML, not INI files.
-  A big focus on writing more `"sans IO" <https://sans-io.readthedocs.io/>`_-style code, and putting some tests around it.
-  Templates and styles now live in a site directory, rather than being a weird
   (and undocumented) mixture of files in the site and in the package.
-  There's no longer a network dependency as part of the build step.
-  Hopefully quite a bit faster, less buggy, and easier to manage.

Documentation is still fairly patchy/non-existent, but I'm trying to reduce the number of undocumented assumptions so that it becomes easy (or possible) for somebody else to reuse it.

2.0.2 (2017-03-25)
------------------

Bugfixes:

-  Stop builds from hanging forever on slow connections.
-  Make ``<pre>`` blocks distinguishable when used in ``<blockquote>``.

2.0.1 (2017-03-24)
------------------

Features:

-  A rudimentary ``newpost`` command for creating a new post with some prefilled
   metadata.

Bugfixes:

-  Add the missing Pygments dependency to syntax highlighting is applied to
   code blocks.

2.0.0 (2017-03-21)
------------------

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
