import re

import requests
import urlpath
from lxml import html

REPLACE_PATTERN = re.compile(r'(?<![A-Za-zА-Яа-яЁё\-_])([A-Za-zА-Яа-яЁё]{6})(?![A-Za-zА-Яа-яЁё\-_™])')


class SiteProxy:
    def __init__(self, origin: str):
        self.origin = urlpath.URL(origin)

    def request_page(self, path: str) -> str:
        url = str(self.origin.joinpath(path))
        response = requests.get(url)
        return response.content.decode('utf-8')

    def process_text(self, text: str) -> str:
        # Split text by spaces and process each word separately.
        # We _could_ apply regexp to the whole string, but this brings problems in some cases,
        # for example, when we have urls.
        chunks = text.split(' ')
        processed_chunks = []
        for chunk in chunks:
            if chunk.startswith('http'):
                # We don't want to touch urls, otherwise they'll become broken.
                processed_chunks.append(chunk)
            else:
                processed_chunks.append(REPLACE_PATTERN.sub(r'\1™', chunk))
        return ' '.join(processed_chunks)

    def process_url(self, url_to_process: str) -> str:
        url = urlpath.URL(url_to_process)
        if url.hostinfo == self.origin.hostinfo:
            return str(url.with_components(scheme='http', hostname='{{ origin }}'))
        elif not url.hostinfo and url.parts[0] == self.origin.hostinfo:
            # Url does not have schema, but is not relative
            return str(url.with_components(
                scheme='http',
                hostname='{{ origin }}',
                path='/'.join(url.parts[1:]),
            ))
        else:
            return url_to_process

    def process_content(self, content: str) -> str:
        # Manually extract doctype, because lxml looses it.
        doctype = None
        doctype_search = re.search(r'<!DOCTYPE (.+?)>', content, flags=re.IGNORECASE)
        if doctype_search:
            doctype = '<!DOCTYPE {0}>'.format(doctype_search.group(1))

        root_element = html.document_fromstring(content)
        self._process_element(root_element)

        processed_content = html.tostring(root_element, encoding='unicode', method='html', doctype=doctype)
        processed_content = self._post_process_content(processed_content)
        return processed_content

    def _process_element_content(self, element: html.HtmlMixin, attribute_name: str) -> None:
        value = getattr(element, attribute_name, None)
        if value is not None:
            setattr(element, attribute_name, self.process_text(value))

    def _process_element_attribute(self, element: html.HtmlMixin, attribute_name: str) -> None:
        if attribute_name in element.attrib:
            element.attrib[attribute_name] = self.process_text(element.attrib[attribute_name])

    def _process_element(self, element: html.HtmlMixin) -> html.HtmlMixin:
        if element.tag in {'style', 'script'} or isinstance(element, html.HtmlComment):
            # Don't process styles, scripts and HTML comments
            # (Even if they have some text to replace, it would require too much efforts to parse it correctly)
            return element
        self._process_element_content(element, 'text')
        self._process_element_content(element, 'tail')
        self._process_element_attribute(element, 'title')
        if element.tag == 'meta':
            self._process_element_attribute(element, 'content')
        for child in element:
            self._process_element(child)
        if element.tag == 'a' and 'href' in element.attrib:
            element.attrib['href'] = self.process_url(element.attrib['href'])
        return element

    def _post_process_content(self, processed_content: str) -> str:
        """Make additional changes for content that has already been processed and converted back to text."""
        # lxml escapes ampersands - we have to restore them manually
        processed_content = processed_content.replace('&amp;', '&')
        # Restore svg viewBox attribute - it is case-sensitive
        processed_content = processed_content.replace('viewbox=', 'viewBox=')
        # Restore non-breaking spaces as named HTML entities
        processed_content = processed_content.replace('\u00a0', '&nbsp;')
        # Unescape urls - Jinja will take care about them
        processed_content = processed_content.replace('%7B%7B%20origin%20%7D%7D', '{{ origin }}')
        # Update static urls
        processed_content = processed_content.replace(
            'https://habr.com/images/1567794742/common-svg-sprite.svg',
            '/static/images/1567794742/common-svg-sprite.svg',
        )
        processed_content = processed_content.replace('url(/fonts', 'url(/static/fonts')
        processed_content = processed_content.replace('href="/images', 'href="/static/images')
        return processed_content
