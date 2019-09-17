import pytest
from hamcrest import assert_that, equal_to, is_


@pytest.mark.parametrize('path', [
    pytest.param('/', id='empty'),
    pytest.param('/news', id='single_chunk_no_trailing_slash'),
    pytest.param('/news/', id='single_chunk_with_trailing_slash'),
    pytest.param('/news/2019', id='multiple_chunks_no_trailing_slash'),
    pytest.param('/news/2019/', id='multiple_chunks_with_trailing_slash'),
])
def test_view_works_for_any_url(client, path):
    response = client.get(path)

    assert_that(response.status_code, is_(equal_to(200)))
