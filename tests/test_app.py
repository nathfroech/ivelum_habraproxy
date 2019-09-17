from hamcrest import assert_that, is_in

from habraproxy.app import app


def test_urls_registered():
    # Just check that module works without any syntax/import/etc. errors
    assert_that('habr_proxy', is_in(app.url_map._rules_by_endpoint))
