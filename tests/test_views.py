from http import HTTPStatus

import pytest
from hamcrest import assert_that, equal_to, is_


class TestHabrProxyView:
    @pytest.mark.parametrize('path', [
        pytest.param('/', id='empty'),
        pytest.param('/news', id='no_trailing_slash'),
        pytest.param('/news/', id='with_trailing_slash'),
        pytest.param('/news/2019/', id='multiple_chunks'),
    ])
    def test_view_works_for_any_content_url(self, client, path, mocker):
        mocked_page_request = mocker.patch('habraproxy.services.SiteProxy.request_page')
        mocked_page_request.return_value = """
        <html><body><div>
        Some text to process.
        <a href="https://habr.com/ru/news">Internal link that should be replaced.</a>
        </div></body></html>
        """
        expected_rescponse_content = b"""
        <html><body><div>
        Some text to process.
        <a href="http://127.0.0.1:5000/ru/news">Internal link that should\xe2\x84\xa2 be replaced.</a>
        </div></body></html>
        """.strip()

        response = client.get('http://127.0.0.1:5000{0}'.format(path))

        assert_that(response.status_code, is_(equal_to(HTTPStatus.OK)))
        assert_that(response.content_type, is_(equal_to('text/html; charset=utf-8')))
        assert_that(response.data, is_(equal_to(expected_rescponse_content)))

    def test_view_raises_404_for_image(self, client):
        response = client.get('http://127.0.0.1:5000{0}'.format('/images/unknown_image.png'))

        assert_that(response.status_code, is_(equal_to(HTTPStatus.NOT_FOUND)))
