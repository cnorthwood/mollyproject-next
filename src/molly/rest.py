import os

from flask import Flask

from molly.flask_support import NegativeFloatConverter
from molly.config import ConfigLoader
from molly.apps.homepage import App as Homepage


def configure_flask_app():
    flask_app = Flask('molly')
    flask_app.url_map.converters['float'] = NegativeFloatConverter

    with open(os.environ.get('MOLLY_CONFIG', 'conf/default.conf')) as fd:
        config_loader = ConfigLoader(flask_app)
        with flask_app.app_context():
            apps, services = config_loader.load_from_config(fd)

    for service in services.values():
        for dependent_service_name, dependent_service in services.iteritems():
            if hasattr(service, 'init_{0}'.format(dependent_service_name)):
                getattr(service, 'init_{0}'.format(dependent_service_name))(dependent_service)

    for app in apps:
        flask_app.register_blueprint(app.blueprint, url_prefix='/' + app.instance_name)
    flask_app.register_blueprint(Homepage(apps).blueprint)

    return flask_app, services['cli']


def start_debug(address=None):
    flask_app.debug = True
    flask_app.run(debug=True, host=address, port=8000)

flask_app, cli_manager = configure_flask_app()