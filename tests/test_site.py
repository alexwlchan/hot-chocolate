# -*- encoding: utf-8

import pytest

from hotchocolate import site

# Only methods that have been migrated to site.py will be tested, so
# there's no risk of conflict with the class in __init__.py.
Site = site.NewSite


def test_create_site_builds_right_directories(tmpdir):
    site.create_site(str(tmpdir))
    for dirname in ['pages', 'posts', 'static', 'styles', 'templates']:
        assert tmpdir.join(dirname).exists()
    assert tmpdir.join('settings.toml').exists()


class TestAddingCSStoHTML:

    @pytest.mark.parametrize('css_string', [
        '',
        'strong { color: red; }',
        '@media screen and (min-width: 500px) { em { color: green; } }',
    ])
    def test_with_css_that_makes_no_change(self, css_string):
        site = Site()
        site._prepared_html = {
            '/': '<html><!-- hc_css_include --><body><p>hello world</p></body></html>'
        }
        site.add_css_to_html(css_string=css_string)
        assert site._prepared_html['/'] == '<html><body><p>hello world</p></body></html>'

    def test_inserting_relevant_css(self):
        site = Site()
        site._prepared_html = {
            '/': '<html><head><!-- hc_css_include --></head><body><p>hello world</p></body></html>'
        }
        site.add_css_to_html(css_string='p { color: red; }')
        assert site._prepared_html['/'] == '<html><head><style>p { color: red; }</style></head><body><p>hello world</p></body></html>'

    def test_inserting_mixed_css(self):
        site = Site()
        site._prepared_html = {
            '/': '<html><head><!-- hc_css_include --></head><body><p>hello world</p></body></html>'
        }
        site.add_css_to_html(css_string='em { color: green; } p { color: red; } strong { color: yellow; }')
        assert site._prepared_html['/'] == '<html><head><style> p { color: red; }</style></head><body><p>hello world</p></body></html>'
