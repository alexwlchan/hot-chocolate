# -*- encoding: utf-8

import glob
import os
import sys

import markdown


class MarkdownExtensionMixin(markdown.Extension):
    """Stub class for importing additional Markdown extensions."""
    pass


def load_plugins(plugin_dir):
    """Load any plugins from the plugin directory."""
    orig_path = list(sys.path)
    sys.path.append(os.path.basename(plugin_dir))
    for path in glob.iglob('%s/*.py' % plugin_dir):
        __import__(os.path.basename(path).replace('.py', ''))
    sys.path = orig_path


def load_markdown_extensions():
    """Return any ``MarkdownExtension`` plugins."""
    load_plugins(os.path.join(os.path.abspath(os.curdir), 'plugins'))
    return [e() for e in MarkdownExtensionMixin.__subclasses__()]
