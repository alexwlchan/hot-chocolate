# -*- encoding: utf-8 -*-

import pytest

from hotchocolate import utils


@pytest.mark.parametrize('xml_string, minified_string', [
    (
        '<root>  <a/>   <b>  </b>     </root>',
        '<root><a/><b/></root>'
    ),
    (
        '<root>  <a/>   <b>data</b>     </root>',
        '<root><a/><b>data</b></root>'
    ),
])
def test_xml_minify(xml_string, minified_string):
    assert utils.minify_xml(xml_string) == minified_string
