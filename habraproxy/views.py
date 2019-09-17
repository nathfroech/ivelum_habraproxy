from flask.views import MethodView


class HabrProxyView(MethodView):
    def get(self, path):
        return 'Hello, world!\n{0}'.format(path)
