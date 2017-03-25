# -*- encoding: utf-8

import os

MARKDOWN_EXTENSIONS = ('.txt', '.md', '.mdown', '.markdown')


def read_isolate_file(site_dir):
    try:
        with open(os.path.join(site_dir, '.isolate')) as f:
            name = f.read().strip()
        return name or None
    except FileNotFoundError:
        pass


def _get_files(site_dir, subdir):
    isolated = read_isolate_file(site_dir)
    if (isolated is not None) and (subdir not in isolated):
        return

    for root, _, filenames in os.walk(os.path.join(site_dir, subdir)):
        for f in filenames:
            if f.lower().endswith(MARKDOWN_EXTENSIONS):
                if (isolated is None) or (isolated.endswith(f)):
                    yield os.path.join(root, f)


def list_post_files(site_dir):
    yield from _get_files(site_dir, subdir='posts')


def list_page_files(site_dir):
    yield from _get_files(site_dir, subdir='pages')
