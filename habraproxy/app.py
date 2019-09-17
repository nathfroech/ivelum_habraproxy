from flask import Flask

from habraproxy import views

app = Flask('habraproxy')

app.add_url_rule('/', defaults={'path': ''}, view_func=views.HabrProxyView.as_view('habr_proxy_main'))
app.add_url_rule('/<path:path>', view_func=views.HabrProxyView.as_view('habr_proxy'))
