from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings
from dependency_injector.providers import Singleton
import tempfile
import os

from openra.containers import container
from openra.models import Maps, Engines
from openra.tests.factories import MapsFactory, UserFactory, EngineFactory
from openra.tests.routes.test_route_base import TestRouteBase
from openra.fakes.docker import FakeDocker
from openra.fakes.engine_file_repository import FakeEngineFileRepository
from openra.fakes.map_upload_orchestrator import FakeMapUploadOrchestrator
from openra.fakes.uploaded_file_importer import FakeUploadedFileImporter
from openra.fakes.map_file_extractor import FakeMapFileExtractor


class TestRouteUploadMap(TestRouteBase):

    _route = '/upload/map'

    def __get_sample_map_file(self):
        """Create a mock .oramap file for testing"""
        # Create a temporary zip file that simulates an oramap
        with tempfile.NamedTemporaryFile(suffix='.oramap', delete=False) as temp_file:
            temp_file.write(b'mock oramap content')
            temp_file.flush()

            with open(temp_file.name, 'rb') as file:
                data = file.read()

            os.unlink(temp_file.name)

        return SimpleUploadedFile(
            'test_map.oramap',
            data,
            content_type='application/zip'
        )

    def test_route_redirects_to_maps_if_not_authed(self):
        # Override Docker-dependent services
        container.reset_singletons()
        overrides = container.override_providers(
            docker=Singleton(FakeDocker),
            engine_file_repository=Singleton(FakeEngineFileRepository),
            map_upload_orchestrator=Singleton(FakeMapUploadOrchestrator),
            uploaded_file_importer=Singleton(FakeUploadedFileImporter),
            map_file_extractor=Singleton(FakeMapFileExtractor)
        )

        try:
            response = self.get({})

            self.assertEquals(302, response.status_code)
            self.assertEquals('/maps/', response.url)
        finally:
            overrides.__exit__()

    def test_route_redirects_to_maps_if_post_not_authed(self):
        # Override Docker-dependent services
        container.reset_singletons()
        overrides = container.override_providers(
            docker=Singleton(FakeDocker),
            engine_file_repository=Singleton(FakeEngineFileRepository),
            map_upload_orchestrator=Singleton(FakeMapUploadOrchestrator),
            uploaded_file_importer=Singleton(FakeUploadedFileImporter),
            map_file_extractor=Singleton(FakeMapFileExtractor)
        )

        try:
            engine = EngineFactory()

            response = self.post({
                'file': self.__get_sample_map_file(),
                'parser': engine.version,
                'info': 'Test map description',
                'policy_cc': 'cc_yes',
                'commercial': 'com_no',
                'adaptations': 'adapt_yes'
            })

            self.assertEquals(302, response.status_code)
            self.assertEquals('/maps/', response.url)
        finally:
            overrides.__exit__()

    def test_route_shows_upload_form_to_authenticated_old_user(self):
        # Override Docker-dependent services
        container.reset_singletons()
        overrides = container.override_providers(
            docker=Singleton(FakeDocker),
            engine_file_repository=Singleton(FakeEngineFileRepository),
            map_upload_orchestrator=Singleton(FakeMapUploadOrchestrator),
            uploaded_file_importer=Singleton(FakeUploadedFileImporter),
            map_file_extractor=Singleton(FakeMapFileExtractor)
        )

        try:
            user = self.create_old_user()
            response = self.get_authed({}, user)

            self.assert_contains(
                response,
                contents=[
                    'Upload your ORAMAP',
                    'type="file"',
                    'Parse with OpenRA version',
                    'Creative Commons'
                ],
                title='Uploading Map'
            )
        finally:
            overrides.__exit__()

    def test_route_blocks_new_users(self):
        # Override Docker-dependent services
        container.reset_singletons()
        overrides = container.override_providers(
            docker=Singleton(FakeDocker),
            engine_file_repository=Singleton(FakeEngineFileRepository),
            map_upload_orchestrator=Singleton(FakeMapUploadOrchestrator),
            uploaded_file_importer=Singleton(FakeUploadedFileImporter),
            map_file_extractor=Singleton(FakeMapFileExtractor)
        )

        try:
            user = UserFactory()  # New user (less than 24 hours old)
            response = self.get_authed({}, user)

            self.assert_contains(
                response,
                contents=[
                    'Action Failed',
                    'User accounts must be one day old'
                ],
                title='Action Blocked'
            )
        finally:
            overrides.__exit__()

    @override_settings(SITE_MAINTENANCE=True)
    def test_route_shows_maintenance_page_when_maintenance_enabled(self):
        user = self.create_old_user()
        response = self.get_authed({}, user)

        self.assert_contains(
            response,
            contents=['Site is under maintenance'],
            status_code=503
        )

    def test_invalid_parser_shows_error_message(self):
        # Override Docker-dependent services
        container.reset_singletons()
        overrides = container.override_providers(
            docker=Singleton(FakeDocker),
            engine_file_repository=Singleton(FakeEngineFileRepository),
            map_upload_orchestrator=Singleton(FakeMapUploadOrchestrator),
            uploaded_file_importer=Singleton(FakeUploadedFileImporter),
            map_file_extractor=Singleton(FakeMapFileExtractor)
        )

        try:
            user = self.create_old_user()

            response = self.post_authed({
                'file': self.__get_sample_map_file(),
                'parser': 'nonexistent-parser',
                'info': 'Test description'
            }, user)

            self.assert_contains(
                response,
                contents=[
                    'Invalid parser selected',
                    'Uploading Map'
                ],
                title='Uploading Map'
            )
        finally:
            overrides.__exit__()

    def test_route_shows_parsers_from_engines_table(self):
        # Override Docker-dependent services
        container.reset_singletons()
        overrides = container.override_providers(
            docker=Singleton(FakeDocker),
            engine_file_repository=Singleton(FakeEngineFileRepository),
            map_upload_orchestrator=Singleton(FakeMapUploadOrchestrator),
            uploaded_file_importer=Singleton(FakeUploadedFileImporter),
            map_file_extractor=Singleton(FakeMapFileExtractor)
        )

        try:
            user = self.create_old_user()

            # Create multiple engines
            engine1 = EngineFactory(version='release-20230101')
            engine2 = EngineFactory(version='release-20231010')
            engine3 = EngineFactory(version='playtest-20240101')

            response = self.get_authed({}, user)

            # Check that all parser options are displayed
            self.assert_contains(
                response,
                contents=[
                    engine1.version,
                    engine2.version,
                    engine3.version
                ]
            )
        finally:
            overrides.__exit__()

    def test_route_handles_policy_options_correctly(self):
        """Test that all policy combinations are handled properly"""
        # Override Docker-dependent services
        container.reset_singletons()
        overrides = container.override_providers(
            docker=Singleton(FakeDocker),
            engine_file_repository=Singleton(FakeEngineFileRepository),
            map_upload_orchestrator=Singleton(FakeMapUploadOrchestrator),
            uploaded_file_importer=Singleton(FakeUploadedFileImporter),
            map_file_extractor=Singleton(FakeMapFileExtractor)
        )

        try:
            user = self.create_old_user()

            response = self.get_authed({}, user)

            # Check that Creative Commons policy options are displayed
            self.assert_contains(
                response,
                contents=[
                    'Creative Commons',
                    'commercial uses',
                    'modifications'
                ]
            )
        finally:
            overrides.__exit__()
