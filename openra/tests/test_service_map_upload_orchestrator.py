from unittest import TestCase
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from django.utils import timezone
import hashlib

from openra.models import Maps
from openra.classes.file_location import FileLocation
from openra.classes.extracted_map import ExtractedMap
from openra.classes.map_hash import MapHash
from openra.services.map_upload_orchestrator import (
    MapUploadOrchestrator,
    ExceptionMapUploadMetadataInvalid,
    ExceptionMapUploadFileStorageFailed
)
from openra.services.map_database_service import (
    MapDatabaseService,
    ExceptionMapAlreadyExists,
    ExceptionMapMetadataMissing
)
from openra.services.map_file_repository import MapFileRepository, ExceptionMapFileStorageFailed
from openra.services.utility.map_hash import MapHashCommand, MapHashTranslator
from openra.services.docker import Docker
from openra.tests.factories import UserFactory


class TestServiceMapUploadOrchestrator(TestCase):

    # Class variable to track unique hash generation
    _hash_counter = 0

    @classmethod
    def get_unique_hash(cls):
        """Generate a unique 40-character hash for testing"""
        cls._hash_counter += 1
        return hashlib.sha1(str(cls._hash_counter).encode()).hexdigest()

    def setUp(self):
        # Create mock dependencies
        self.mock_map_database_service = Mock(spec=MapDatabaseService)
        self.mock_map_file_repository = Mock(spec=MapFileRepository)
        self.mock_map_hash_command = Mock(spec=MapHashCommand)
        self.mock_map_hash_translator = Mock(spec=MapHashTranslator)
        self.mock_docker = Mock(spec=Docker)

        # Create orchestrator with mocked dependencies
        self.orchestrator = MapUploadOrchestrator(
            map_database_service=self.mock_map_database_service,
            map_file_repository=self.mock_map_file_repository,
            map_hash_command=self.mock_map_hash_command,
            map_hash_translator=self.mock_map_hash_translator,
            docker=self.mock_docker
        )

        # Create test user
        self.user = UserFactory()

        # Sample test data
        self.valid_metadata = {
            'title': 'Test Map',
            'author': 'Test Author',
            'categories': ['Test'],
            'players': 2,
            'game_mod': 'ra',
            'width': 64,
            'height': 64,
            'bounds': '0,0,64,64',
            'mapformat': 12,
            'spawnpoints': '10,10, 50,50',
            'tileset': 'temperate',
            'base64_players': 'dGVzdA==',
            'lua': False
        }

        self.valid_policy = {
            'cc': True,
            'commercial': False,
            'adaptations': 'yes'
        }

        # Create mock file location and extracted map
        self.mock_map_file_location = Mock(spec=FileLocation)
        self.mock_extracted_map_location = Mock(spec=FileLocation)
        self.mock_extracted_map = Mock(spec=ExtractedMap)
        self.mock_extracted_map.location = self.mock_extracted_map_location

    def test_upload_map_completes_successfully(self):
        # Setup - configure mocks for successful upload
        map_hash_output = "test_hash_output"
        map_hash = MapHash(self.get_unique_hash())

        # Create a mock Maps record
        mock_map_record = Mock(spec=Maps)
        mock_map_record.id = 123
        mock_map_record.map_hash = map_hash.map_hash
        mock_map_record.title = 'Test Map'
        mock_map_record.delete = Mock()  # Add delete method for cleanup testing

        # Configure mocks
        self.mock_map_hash_command.run_command.return_value = map_hash_output
        self.mock_map_hash_translator.translate.return_value = map_hash
        self.mock_extracted_map.parse_metadata.return_value = self.valid_metadata
        self.mock_map_database_service.save_map_record.return_value = mock_map_record
        self.mock_map_file_repository.store_map.return_value = None

        # Execute
        result = self.orchestrator.upload_map(
            map_file_location=self.mock_map_file_location,
            extracted_map=self.mock_extracted_map,
            user=self.user,
            parser='release-20231010',
            description='Test description',
            policy=self.valid_policy,
            revision=1,
            previous_revision_id=0
        )

        # Assert
        self.assertEqual(result, mock_map_record)

        # Verify the orchestrator called all components correctly
        self.mock_map_hash_command.run_command.assert_called_once()
        self.mock_map_hash_translator.translate.assert_called_once_with(map_hash_output)
        self.mock_extracted_map.parse_metadata.assert_called_once()

        self.mock_map_database_service.save_map_record.assert_called_once_with(
            map_hash=map_hash,
            metadata=self.valid_metadata,
            user=self.user,
            parser='release-20231010',
            description='Test description',
            policy=self.valid_policy,
            revision=1,
            previous_revision_id=0
        )

        self.mock_map_file_repository.store_map.assert_called_once_with(
            map_id=123,
            map_file_location=self.mock_map_file_location,
            extracted_map_location=self.mock_extracted_map_location
        )

    def test_upload_map_throws_exception_when_metadata_parsing_fails(self):
        # Setup - metadata parsing returns None/empty
        map_hash_output = "test_hash_output"
        map_hash = MapHash(self.get_unique_hash())

        self.mock_map_hash_command.run_command.return_value = map_hash_output
        self.mock_map_hash_translator.translate.return_value = map_hash
        self.mock_extracted_map.parse_metadata.return_value = None  # Simulate parsing failure

        # Execute & Assert
        with self.assertRaises(ExceptionMapUploadMetadataInvalid) as context:
            self.orchestrator.upload_map(
                map_file_location=self.mock_map_file_location,
                extracted_map=self.mock_extracted_map,
                user=self.user,
                parser='release-20231010',
                description='Test description',
                policy=self.valid_policy
            )

        # Check exception details
        exception = context.exception
        self.assertEqual(exception.message, "Unable to parse map metadata")

        # Verify that database service was never called (early exit)
        self.mock_map_database_service.save_map_record.assert_not_called()
        self.mock_map_file_repository.store_map.assert_not_called()

    def test_upload_map_throws_exception_when_metadata_parsing_returns_empty_dict(self):
        # Setup - metadata parsing returns empty dict
        map_hash_output = "test_hash_output"
        map_hash = MapHash(self.get_unique_hash())

        self.mock_map_hash_command.run_command.return_value = map_hash_output
        self.mock_map_hash_translator.translate.return_value = map_hash
        self.mock_extracted_map.parse_metadata.return_value = {}  # Empty dict is falsy

        # Execute & Assert
        with self.assertRaises(ExceptionMapUploadMetadataInvalid) as context:
            self.orchestrator.upload_map(
                map_file_location=self.mock_map_file_location,
                extracted_map=self.mock_extracted_map,
                user=self.user,
                parser='release-20231010',
                description='Test description',
                policy=self.valid_policy
            )

        exception = context.exception
        self.assertEqual(exception.message, "Unable to parse map metadata")

    def test_upload_map_propagates_database_service_exceptions(self):
        # Setup - database service throws exception for duplicate hash
        map_hash_output = "test_hash_output"
        map_hash = MapHash(self.get_unique_hash())

        self.mock_map_hash_command.run_command.return_value = map_hash_output
        self.mock_map_hash_translator.translate.return_value = map_hash
        self.mock_extracted_map.parse_metadata.return_value = self.valid_metadata
        self.mock_map_database_service.save_map_record.side_effect = ExceptionMapAlreadyExists(map_hash.map_hash)

        # Execute & Assert
        with self.assertRaises(ExceptionMapAlreadyExists) as context:
            self.orchestrator.upload_map(
                map_file_location=self.mock_map_file_location,
                extracted_map=self.mock_extracted_map,
                user=self.user,
                parser='release-20231010',
                description='Test description',
                policy=self.valid_policy
            )

        # Verify file repository was never called (database failed first)
        self.mock_map_file_repository.store_map.assert_not_called()

    def test_upload_map_propagates_missing_metadata_exceptions(self):
        # Setup - database service throws exception for missing metadata
        map_hash_output = "test_hash_output"
        map_hash = MapHash(self.get_unique_hash())

        self.mock_map_hash_command.run_command.return_value = map_hash_output
        self.mock_map_hash_translator.translate.return_value = map_hash
        self.mock_extracted_map.parse_metadata.return_value = self.valid_metadata
        self.mock_map_database_service.save_map_record.side_effect = ExceptionMapMetadataMissing('title')

        # Execute & Assert
        with self.assertRaises(ExceptionMapMetadataMissing) as context:
            self.orchestrator.upload_map(
                map_file_location=self.mock_map_file_location,
                extracted_map=self.mock_extracted_map,
                user=self.user,
                parser='release-20231010',
                description='Test description',
                policy=self.valid_policy
            )

        # Verify file repository was never called (database failed first)
        self.mock_map_file_repository.store_map.assert_not_called()

    def test_upload_map_cleans_up_database_record_when_file_storage_fails(self):
        # Setup - file storage fails after successful database save
        map_hash_output = "test_hash_output"
        map_hash = MapHash(self.get_unique_hash())

        # Create mock Maps record with delete method
        mock_map_record = Mock(spec=Maps)
        mock_map_record.id = 123
        mock_map_record.delete = Mock()

        self.mock_map_hash_command.run_command.return_value = map_hash_output
        self.mock_map_hash_translator.translate.return_value = map_hash
        self.mock_extracted_map.parse_metadata.return_value = self.valid_metadata
        self.mock_map_database_service.save_map_record.return_value = mock_map_record

        # Make file repository throw an exception
        file_error = ExceptionMapFileStorageFailed(123, "Could not copy file to destination")
        self.mock_map_file_repository.store_map.side_effect = file_error

        # Execute & Assert
        with self.assertRaises(ExceptionMapUploadFileStorageFailed) as context:
            self.orchestrator.upload_map(
                map_file_location=self.mock_map_file_location,
                extracted_map=self.mock_extracted_map,
                user=self.user,
                parser='release-20231010',
                description='Test description',
                policy=self.valid_policy
            )

        # Check exception details
        exception = context.exception
        self.assertEqual(exception.message, "Map upload failed during file storage")
        # The exception detail will contain the string representation of the nested exception
        self.assertIn("Could not copy file to destination", exception.detail[0])

        # Verify database record was cleaned up
        mock_map_record.delete.assert_called_once()

    def test_upload_map_cleans_up_database_record_when_generic_file_storage_exception_occurs(self):
        # Setup - generic exception from file storage
        map_hash_output = "test_hash_output"
        map_hash = MapHash(self.get_unique_hash())

        # Create mock Maps record with delete method
        mock_map_record = Mock(spec=Maps)
        mock_map_record.id = 123
        mock_map_record.delete = Mock()

        self.mock_map_hash_command.run_command.return_value = map_hash_output
        self.mock_map_hash_translator.translate.return_value = map_hash
        self.mock_extracted_map.parse_metadata.return_value = self.valid_metadata
        self.mock_map_database_service.save_map_record.return_value = mock_map_record

        # Make file repository throw a generic exception
        self.mock_map_file_repository.store_map.side_effect = Exception("Disk full")

        # Execute & Assert
        with self.assertRaises(ExceptionMapUploadFileStorageFailed) as context:
            self.orchestrator.upload_map(
                map_file_location=self.mock_map_file_location,
                extracted_map=self.mock_extracted_map,
                user=self.user,
                parser='release-20231010',
                description='Test description',
                policy=self.valid_policy
            )

        # Check exception details
        exception = context.exception
        self.assertEqual(exception.message, "Map upload failed during file storage")
        self.assertIn("error: Disk full", exception.detail)

        # Verify database record was cleaned up
        mock_map_record.delete.assert_called_once()

    def test_upload_map_with_custom_revision_and_previous_revision(self):
        # Setup - test with custom revision parameters
        map_hash_output = "test_hash_output"
        map_hash = MapHash(self.get_unique_hash())

        mock_map_record = Mock(spec=Maps)
        mock_map_record.id = 456
        mock_map_record.revision = 2
        mock_map_record.pre_rev = 123
        mock_map_record.delete = Mock()

        self.mock_map_hash_command.run_command.return_value = map_hash_output
        self.mock_map_hash_translator.translate.return_value = map_hash
        self.mock_extracted_map.parse_metadata.return_value = self.valid_metadata
        self.mock_map_database_service.save_map_record.return_value = mock_map_record
        self.mock_map_file_repository.store_map.return_value = None

        # Execute with custom revision parameters
        result = self.orchestrator.upload_map(
            map_file_location=self.mock_map_file_location,
            extracted_map=self.mock_extracted_map,
            user=self.user,
            parser='release-20231010',
            description='Test description',
            policy=self.valid_policy,
            revision=2,
            previous_revision_id=123
        )

        # Assert
        self.assertEqual(result, mock_map_record)

        # Verify database service was called with correct revision parameters
        self.mock_map_database_service.save_map_record.assert_called_once_with(
            map_hash=map_hash,
            metadata=self.valid_metadata,
            user=self.user,
            parser='release-20231010',
            description='Test description',
            policy=self.valid_policy,
            revision=2,
            previous_revision_id=123
        )

    def test_upload_map_uses_default_revision_parameters_when_not_provided(self):
        # Setup - test default parameters
        map_hash_output = "test_hash_output"
        map_hash = MapHash(self.get_unique_hash())

        mock_map_record = Mock(spec=Maps)
        mock_map_record.id = 789
        mock_map_record.delete = Mock()

        self.mock_map_hash_command.run_command.return_value = map_hash_output
        self.mock_map_hash_translator.translate.return_value = map_hash
        self.mock_extracted_map.parse_metadata.return_value = self.valid_metadata
        self.mock_map_database_service.save_map_record.return_value = mock_map_record
        self.mock_map_file_repository.store_map.return_value = None

        # Execute without specifying revision parameters
        result = self.orchestrator.upload_map(
            map_file_location=self.mock_map_file_location,
            extracted_map=self.mock_extracted_map,
            user=self.user,
            parser='release-20231010',
            description='Test description',
            policy=self.valid_policy
        )

        # Assert
        self.assertEqual(result, mock_map_record)

        # Verify database service was called with default revision parameters
        self.mock_map_database_service.save_map_record.assert_called_once_with(
            map_hash=map_hash,
            metadata=self.valid_metadata,
            user=self.user,
            parser='release-20231010',
            description='Test description',
            policy=self.valid_policy,
            revision=1,
            previous_revision_id=0
        )

    def test_orchestrator_initializes_with_all_dependencies(self):
        # Test that orchestrator properly stores all injected dependencies
        orchestrator = MapUploadOrchestrator(
            map_database_service=self.mock_map_database_service,
            map_file_repository=self.mock_map_file_repository,
            map_hash_command=self.mock_map_hash_command,
            map_hash_translator=self.mock_map_hash_translator,
            docker=self.mock_docker
        )

        self.assertEqual(orchestrator.map_database_service, self.mock_map_database_service)
        self.assertEqual(orchestrator.map_file_repository, self.mock_map_file_repository)
        self.assertEqual(orchestrator.map_hash_command, self.mock_map_hash_command)
        self.assertEqual(orchestrator.map_hash_translator, self.mock_map_hash_translator)
        self.assertEqual(orchestrator.docker, self.mock_docker)

    def test_exception_map_upload_metadata_invalid_has_correct_message(self):
        # Test the custom exception class
        exception = ExceptionMapUploadMetadataInvalid()
        self.assertEqual(exception.message, "Unable to parse map metadata")

    def test_exception_map_upload_file_storage_failed_has_correct_message_and_details(self):
        # Test the custom exception class with error details
        error_message = "Permission denied when copying file"
        exception = ExceptionMapUploadFileStorageFailed(error_message)

        self.assertEqual(exception.message, "Map upload failed during file storage")
        self.assertIn('error: ' + error_message, exception.detail)
