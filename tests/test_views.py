import pytest
from hamcrest import assert_that, equal_to, is_


@pytest.mark.parametrize('path', [
    pytest.param('/', id='empty'),
    pytest.param('/news', id='no_trailing_slash'),
    pytest.param('/news/', id='with_trailing_slash'),
    pytest.param('/news/2019/', id='multiple_chunks'),
])
def test_view_works_for_any_url(client, path, mocker):
    mocked_page_request = mocker.patch('habraproxy.services.SiteProxy.request_page')
    mocked_page_request.return_value = '<html><body><div>Some text to process. abcdef</div></body></html>'

    response = client.get(path)

    assert_that(response.status_code, is_(equal_to(200)))
    assert_that(response.content_type, is_(equal_to('text/html; charset=utf-8')))
    assert_that(
        response.data,
        is_(equal_to(b'<html><body><div>Some text to process. abcdef\xe2\x84\xa2</div></body></html>')),
    )
