from importlib import import_module
import os

from flask.ext.script import Manager
from gunicorn.app.base import Application

def configure_manager(flask_app, debug, default_port=8000):
    manager = Manager(flask_app, with_default_commands=False)

    @manager.command
    def start(port=default_port):
        class MollyApplication(Application):

            def init(self, parser, opts, args):
                self.cfg.set('bind', '127.0.0.1:{}'.format(port))

            def load(self):
                return flask_app

        MollyApplication().run()

    if debug is not None:
        manager.command(debug)

    return manager

def rest_main():
    from molly.rest import flask_app, start_debug
    configure_manager(flask_app, start_debug).run()

def ui_main():
    package, app_name = os.environ.get('MOLLY_UI_MODULE', 'molly.ui.html5.server:flask_app').split(':', 1)
    module = import_module(package)
    configure_manager(getattr(module, app_name), getattr(module, 'start_debug'), 8002).run()
