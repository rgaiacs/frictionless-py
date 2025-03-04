import multiprocessing
from ...server import Server
from ... import helpers
from ... import settings
from ... import actions


class ApiServer(Server):
    """API server implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.server import ApiParser`

    """

    def start(self, *, port):
        app = create_api()
        server = create_server(app, port=port)
        server.run()


# Internal


def create_api():
    flask = helpers.import_from_plugin("flask", plugin="server")

    # Create api
    app = flask.Flask("app")

    @app.route("/")
    def api_main():
        options = ["/describe", "/extract", "/validate", "/transform"]
        return flask.jsonify({"version": settings.VERSION, "options": options})

    @app.route("/describe", methods=["POST"])
    def api_describe():
        options = helpers.create_options(flask.request.json)
        metadata = actions.describe(**options)
        return flask.jsonify(metadata)

    @app.route("/extract", methods=["POST"])
    def api_extract():
        options = helpers.create_options(flask.request.json)
        options["process"] = lambda row: row.to_dict(json=True)
        data = actions.extract(**options)
        return flask.jsonify(data)

    @app.route("/validate", methods=["POST"])
    def api_validate():
        options = helpers.create_options(flask.request.json)
        report = actions.validate(**options)
        return flask.jsonify(report)

    @app.route("/transform", methods=["POST"])
    def api_transform():
        options = helpers.create_options(flask.request.json)
        actions.transform(**options)
        return flask.jsonify({"success": True})

    return app


def create_server(app, *, port):
    # https://docs.gunicorn.org/en/latest/custom.html
    base = helpers.import_from_plugin("gunicorn.app.base", plugin="server")

    # Define server
    class Server(base.BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()

        def load_config(self):
            config = {
                key: value
                for key, value in self.options.items()
                if key in self.cfg.settings and value is not None
            }
            for key, value in config.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    # Define options
    options = {
        "bind": "%s:%s" % ("127.0.0.1", str(port)),
        "workers": multiprocessing.cpu_count() + 1,
        "accesslog": "-",
    }

    # Return server
    server = Server(app, options)
    return server
