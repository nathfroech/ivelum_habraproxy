from flask import render_template_string
from flask.views import MethodView

from habraproxy.services import SiteProxy


class HabrProxyView(MethodView):
    def get(self, path):
        site_proxy = SiteProxy('https://habr.com')
        original_content = site_proxy.request_page(path)
        processed_content = site_proxy.process_content(original_content)
        return render_template_string(processed_content)
