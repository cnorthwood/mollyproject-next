from flask import Blueprint, Flask
from mock import Mock, sentinel, MagicMock
import unittest2

from flask.ext.script import Command

from molly.apps import places

class TestPlacesApp(unittest2.TestCase):

    def setUp(self):
        self._mock_cli_service = Mock()
        self._mock_tasks_service = Mock()
        self._mock_importer = Mock()
        self._mock_importer.IMPORTER_NAME = 'test'
        self._mock_importer.IMPORT_SCHEDULE = sentinel.schedule
        self._app = places.App(
            'places', {}, [self._mock_importer],
            {'cli': self._mock_cli_service, 'tasks': self._mock_tasks_service, 'kv': MagicMock(), 'search': Mock()}
        )

    def test_module_uri_is_correct(self):
        self.assertEquals('http://mollyproject.org/apps/places', self._app.module)

    def test_instance_name_is_correct(self):
        self.assertEquals('places', self._app.instance_name)

    def test_importers_are_registered_as_periodic_tasks(self):
        self._mock_tasks_service.periodic_task.assert_called_once_with(
            self._mock_importer.load, crontab=self._mock_importer.IMPORT_SCHEDULE
        )

    def test_importers_are_registered_as_cli_tasks(self):
        self.assertEquals('import_test_places', self._mock_cli_service.add_command.call_args[0][0])
        self.assertIsInstance(self._mock_cli_service.add_command.call_args[0][1], Command)
        self.assertEquals(self._mock_importer.load, self._mock_cli_service.add_command.call_args[0][1].run)

    def test_blueprint_exists(self):
        self.assertIsInstance(self._app.blueprint, Blueprint)

    def test_homepage_includes_link_to_nearby_search(self):
        flask = Flask(__name__)
        flask.register_blueprint(self._app.blueprint, url_prefix="/pois")
        with flask.test_request_context():
            self.assertIn({
                'self': 'http://mollyproject.org/apps/places/nearby',
                'href': '/pois/nearby/{lat},{lon}/'
            }, self._app.links)

    def test_homepage_includes_link_to_free_text_search(self):
        flask = Flask(__name__)
        flask.register_blueprint(self._app.blueprint, url_prefix="/pois")
        with flask.test_request_context():
            self.assertIn({
                'self': 'http://mollyproject.org/apps/places/search',
                'href': 'http://localhost/pois/search'
            }, self._app.links)
