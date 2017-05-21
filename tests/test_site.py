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

    def _add_css_to_html(self, html, css_string):
        site = Site()
        site._prepared_html = {'/': html}
        site.add_css_to_html(css_string=css_string)
        return site._prepared_html['/']

    @pytest.mark.parametrize('css_string', [
        '',
        'strong { color: red; }',
        '@media screen and (min-width: 500px) { em { color: green; } }',
    ])
    def test_with_css_that_makes_no_change(self, css_string):
        result = self._add_css_to_html(
            html='<html><!-- hc_css_include --><body><p>hello world</p></body></html>',
            css_string=css_string
        )
        assert result == '<html><body><p>hello world</p></body></html>'

    def test_inserting_relevant_css(self):
        result = self._add_css_to_html(
            html='<html><head><!-- hc_css_include --></head><body><p>hello world</p></body></html>',
            css_string='p { color: red; }'
        )
        assert result == '<html><head><style>p { color: red; }</style></head><body><p>hello world</p></body></html>'

    def test_inserting_mixed_css(self):
        result = self._add_css_to_html(
            html='<html><head><!-- hc_css_include --></head><body><p>hello world</p></body></html>',
            css_string='em { color: green; } p { color: red; } strong { color: yellow; }'
        )
        assert result == '<html><head><style> p { color: red; }</style></head><body><p>hello world</p></body></html>'

    def test_proper_body_finding(self):
        # This is a check that I'm using a proper HTML parser to find the
        # body HTML, not just a regex or something.
        result = self._add_css_to_html(
            html='<html><head><!-- hc_css_include --></head><body id="foo"><p>hello world</p></body></html>',
            css_string='em { color: green; } p { color: red; } strong { color: yellow; }'
        )
        assert result == '<html><head><style> p { color: red; }</style></head><body id="foo"><p>hello world</p></body></html>'
