from http import HTTPStatus
from typing import Any

from flask import abort, jsonify, render_template_string, request
from flask.views import MethodView

from habraproxy.services import SiteProxy


class HabrProxyView(MethodView):
    def get(self, path: str) -> Any:
        if path.startswith('images/'):
            return abort(HTTPStatus.NOT_FOUND)
        site_proxy = SiteProxy('https://habr.com')
        original_content = site_proxy.request_page(path)
        processed_content = site_proxy.process_content(original_content)
        return render_template_string(processed_content, origin=request.host)


class WebmanifestMockView(MethodView):
    """Just a mock, which returns same data as habr.com itself."""

    def get(self) -> Any:
        data = {
            'name': 'Habr',
            'short_name': 'Habr',
            'icons': [
                {
                    'src': '/images/android-chrome-192x192.png',
                    'sizes': '192x192',
                    'type': 'image/png',
                },
                {
                    'src': '/images/android-chrome-256x256.png',
                    'sizes': '256x256',
                    'type': 'image/png',
                },
            ],
            'theme_color': '#77a2b6',
            'background_color': '#77a2b6',
            'display': 'standalone',
        }
        return jsonify(data)
