import difflib
import pathlib

import pytest
import requests
import requests_mock
from hamcrest import assert_that, equal_to, instance_of, is_
from hamcrest.core.core.isequal import IsEqual
from hamcrest.core.string_description import StringDescription

from habraproxy.services import SiteProxy

FIXTURES_DIR: pathlib.Path = pathlib.Path(__file__).resolve().parent / 'fixtures'


class HasEqualContent(IsEqual):
    def describe_mismatch(self, item: str, mismatch_description: StringDescription) -> None:
        mismatch_description.out = ''
        mismatch_description.append_text('Expected and actual results do not match\n')
        diff = difflib.unified_diff(
            self.object.splitlines(),
            item.splitlines(),
            fromfile='Expected',
            tofile='Actual',
        )
        for line in diff:
            mismatch_description.append_text(line).append_text('\n')


def has_equal_content_to(expected: str) -> HasEqualContent:
    return HasEqualContent(expected)


content_processor_cases = [
    pytest.param(
        '<html><body><div>abcdef ghij klmnopqr</div></body></html>',
        '<html><body><div>abcdef™ ghij klmnopqr</div></body></html>',
        id='simple_text',
    ),
    pytest.param(
        '<html><body><div>abc & def</div></body></html>',
        '<html><body><div>abc & def</div></body></html>',
        id='text_with_ampersand',
    ),
    pytest.param(
        '<html><body><div class="abcdef">Some text</div></body></html>',
        '<html><body><div class="abcdef">Some text</div></body></html>',
        id='class_name',
    ),
    pytest.param(
        '<html><body><button>Press me</button></body></html>',
        '<html><body><button>Press me</button></body></html>',
        id='html_tag',
    ),
    pytest.param(
        '<html><body><a href="" title="abcdef">Follow me</a></body></html>',
        '<html><body><a href="" title="abcdef™">Follow™ me</a></body></html>',
        id='html_tag_title',
    ),
    pytest.param(
        '<html><body><a href="" target="_blank">Follow me</a></body></html>',
        '<html><body><a href="" target="_blank">Follow™ me</a></body></html>',
        id='html_tag_attribute',
    ),
    pytest.param(
        '<html><head><style type="text/css">.abcdef {border: 1px double black;}</style></head><body>Text</body></html>',
        '<html><head><style type="text/css">.abcdef {border: 1px double black;}</style></head><body>Text</body></html>',
        id='styles',
    ),
    pytest.param(
        '<html><head><script>function foobar() {return window.document;}</script></head><body>Text</body></html>',
        '<html><head><script>function foobar() {return window.document;}</script></head><body>Text</body></html>',
        id='scripts',
    ),
    pytest.param(
        '<html><body><a href="https://habr.com/ru/post/467875/">Another page link</a></body></html>',
        '<html><body><a href="http://{{ origin }}/ru/post/467875/">Another page link</a></body></html>',
        id='links_to_other_site_pages',
    ),
    pytest.param(
        """
            <html><head>
            <meta name="description" content="Самое важное из ИТ мира на сегодня: новости науки и высоких технологий, разработки, гаджетов, игр, бизнеса и другие." />
            <meta property="og:site_name" content="Хабр" />
            <meta property="og:title" content="ИТ Новости на Хабре: главные новости технологий"/>
            <meta property="og:description" content="Самое важное из ИТ мира на сегодня: новости науки и высоких технологий, разработки, гаджетов, игр, бизнеса и другие."/>
            </head><body>Text</body></html>
        """,
        """
            <html><head>
            <meta name="description" content="Самое важное™ из ИТ мира на сегодня: новости науки и высоких технологий, разработки, гаджетов, игр, бизнеса и другие™.">
            <meta property="og:site_name" content="Хабр">
            <meta property="og:title" content="ИТ Новости на Хабре: главные новости технологий">
            <meta property="og:description" content="Самое важное™ из ИТ мира на сегодня: новости науки и высоких технологий, разработки, гаджетов, игр, бизнеса и другие™.">
            </head><body>Text</body></html>
        """.strip(),
        id='meta',
    ),
    pytest.param(
        '<html><body><svg xmlns="http://www.w3.org/2000/svg"><path d=""/></svg></body></html>',
        '<html><body><svg xmlns="http://www.w3.org/2000/svg"><path d=""></path></svg></body></html>',
        id='svg_path',
    ),
    pytest.param(
        '<html><body><svg><use xlink:href="https://habr.com/common-svg-sprite.svg"/></svg></body></html>',
        '<html><body><svg><use xlink:href="https://habr.com/common-svg-sprite.svg"></use></svg></body></html>',
        id='svg_use',
    ),
    pytest.param(
        '<html><body><svg><use xlink:href="https://habr.com/images/1567794742/common-svg-sprite.svg#close"/></svg></body></html>',
        '<html><body><svg><use xlink:href="/static/images/1567794742/common-svg-sprite.svg#close"></use></svg></body></html>',
        id='svg_use_href',
    ),
    pytest.param(
        """<html><body><div>
           Уникальное для России ежегодное мероприятие, целиком посвящённое тематике нейрокомпьютерных интерфейсов, пройдёт с 3 по 5 октября 2019 года. Но регистрация для участников закончится уже 25 сентября.
           <br>
           <br>
           Международная конференция «Нейрокомпьютерный интерфейс: Наука и практика» ежегодно проходит в Самаре с 2015 года. Главным организатором традиционно выступают Самарский государственный медицинский университет и компания IT Universe, а поддержку мероприятию оказывают Отраслевой союз «Нейронет» и Правительство Самарской области.
           <br>
           <br>
           Тематика конференции отвечает одному из приоритетных направлений деятельности системы здравоохранения – разработке и внедрению новейших технологий реабилитации: помощи людям с нарушениями двигательных и когнитивных функций, восстановлении после инсультов и других нарушений мозга. Сегодня большая часть таких технологий основана на виртуальной реальности (VR).
           </div></body></html>
        """,
        """<html><body><div>
           Уникальное для России™ ежегодное мероприятие, целиком посвящённое тематике нейрокомпьютерных интерфейсов, пройдёт с 3 по 5 октября 2019 года. Но регистрация для участников закончится уже 25 сентября.
           <br>
           <br>
           Международная конференция «Нейрокомпьютерный интерфейс: Наука и практика» ежегодно проходит в Самаре™ с 2015 года. Главным организатором традиционно выступают Самарский государственный медицинский университет и компания IT Universe, а поддержку мероприятию оказывают Отраслевой союз «Нейронет» и Правительство Самарской области.
           <br>
           <br>
           Тематика конференции отвечает одному™ из приоритетных направлений деятельности системы здравоохранения – разработке и внедрению новейших технологий реабилитации: помощи™ людям с нарушениями двигательных и когнитивных функций, восстановлении после инсультов и других™ нарушений мозга. Сегодня большая часть таких технологий основана на виртуальной реальности (VR).
           </div></body></html>
        """.strip(),
        id='paragraph_with_br_tag',
    ),
    pytest.param(
        '<html><body><div><!-- Yandex.Metrika counter --></div></body></html>',
        '<html><body><div><!-- Yandex.Metrika counter --></div></body></html>',
        id='html_comment',
    ),
    pytest.param(
        '<html><body><div>abc&nbsp;def</div></body></html>',
        '<html><body><div>abc&nbsp;def</div></body></html>',
        id='non_breaking_space',
    ),
    pytest.param(
        FIXTURES_DIR.joinpath('example_response.html').read_text(),
        FIXTURES_DIR.joinpath('example_processed_response.html').read_text().strip(),
        id='real_page',
    ),
]


class TestSiteProxy:
    # Tests for SiteProxy.request_page()
    @pytest.mark.parametrize('path,expected_url', [
        pytest.param('', 'https://habr.com/', id='empty'),
        pytest.param('/', 'https://habr.com/', id='slash'),
        pytest.param('news/', 'https://habr.com/news/', id='no_leading_slash'),
        pytest.param('/news', 'https://habr.com/news', id='no_trailing_slash'),
        pytest.param('/news/', 'https://habr.com/news/', id='with_trailing_slash'),
        pytest.param('/news/2019/', 'https://habr.com/news/2019/', id='multiple_chunks'),
    ])
    def test_joins_url_parts(self, path, expected_url, mocker):
        site_proxy = SiteProxy('https://habr.com')
        page_request_mock = mocker.patch('requests.get')
        dummy_response = requests.Response()
        dummy_response._content = b''  # type: ignore
        page_request_mock.return_value = dummy_response

        site_proxy.request_page('/ru/news/')

        page_request_mock.assert_called_with('https://habr.com/ru/news/')

    def test_method_returns_page_content(self):
        site_proxy = SiteProxy('https://habr.com')
        expected_url = 'https://habr.com/ru/news/'
        mocked_response_content = FIXTURES_DIR.joinpath('example_response.html').read_text()

        with requests_mock.Mocker() as requests_mocker:
            requests_mocker.get(expected_url, text=mocked_response_content)

            page_content = site_proxy.request_page('/ru/news/')

        assert_that(page_content, is_(instance_of(str)))

    # Tests for SiteProxy.process_text()
    @pytest.mark.parametrize('input_text,expected_output', [
        pytest.param('abcdef ghij klmnopqr', 'abcdef™ ghij klmnopqr', id='latin_letters'),
        pytest.param('абвгде жзик лмнопрс', 'абвгде™ жзик лмнопрс', id='cyrillic_letters'),
        pytest.param('абвгдё', 'абвгдё™', id='cyrillic_letters_with_yo'),
        pytest.param('abcdef™', 'abcdef™', id='string_already_has_sign'),
        pytest.param('abcdef-ghijkl', 'abcdef-ghijkl', id='hyphen_between_words'),
        pytest.param('abc-de', 'abc-de', id='hyphen_between_words_6_symbols_total'),
        pytest.param('abcdef_ghijkl', 'abcdef_ghijkl', id='underscore_between_words'),
        pytest.param('abc_de', 'abc_de', id='underscore_between_words_6_symbols_total'),
        pytest.param('пользователей в «Яндекс.Драйве»', 'пользователей в «Яндекс™.Драйве™»', id='dot_between_words'),
        pytest.param('abcdef/ghijkl', 'abcdef™/ghijkl™', id='slash_between_words'),
        pytest.param(
            'Text with url https://www.amazon.com/',
            'Text with url https://www.amazon.com/',
            id='url_in_text_6_symbol_domain',
        ),
        pytest.param(
            'Text with url https://habr.com/abcdef',
            'Text with url https://habr.com/abcdef',
            id='url_in_text_6_symbol_path_element',
        ),
        pytest.param(
            'Text with url https://habr.com/news?abcdef=abcdef',
            'Text with url https://habr.com/news?abcdef=abcdef',
            id='url_in_text_6_symbol_parameter',
        ),
    ])
    def test_text_processed(self, input_text, expected_output):
        site_proxy = SiteProxy('https://habr.com')

        processed_text = site_proxy.process_text(input_text)

        assert_that(processed_text, is_(equal_to(expected_output)))

    # Tests for SiteProxy.process_url()
    @pytest.mark.parametrize('url,expected_output', [
        pytest.param('https://habr.com/ru/post/467875/', 'http://{{ origin }}/ru/post/467875/', id='same_schema'),
        pytest.param('http://habr.com/ru/post/467875/', 'http://{{ origin }}/ru/post/467875/', id='http_vs_https'),
        pytest.param('//habr.com/ru/post/467875/', 'http://{{ origin }}/ru/post/467875/', id='double_slash_start'),
        pytest.param('habr.com/ru/post/467875', 'http://{{ origin }}/ru/post/467875', id='no_schema'),
        pytest.param(
            'https://stackoverflow.com/questions/tagged/python',
            'https://stackoverflow.com/questions/tagged/python',
            id='another_origin',
        ),
        pytest.param('/ru/post/467875/', '/ru/post/467875/', id='relative_url'),
    ])
    def test_url_origin_changed(self, url, expected_output):
        site_proxy = SiteProxy('https://habr.com')

        processed_url = site_proxy.process_url(url)

        assert_that(processed_url, is_(equal_to(expected_output)))

    # Tests for SiteProxy.process_content()
    @pytest.mark.parametrize('input_content,expected_output', content_processor_cases)
    def test_content_changed(self, input_content, expected_output):
        site_proxy = SiteProxy('https://habr.com')

        processed_content = site_proxy.process_content(input_content)

        assert_that(processed_content, has_equal_content_to(expected_output))
