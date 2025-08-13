from unittest import TestCase
from unittest.mock import Mock, patch
from django.contrib.auth.models import User
from django.utils import timezone

from openra.models import Maps
from openra.classes.map_hash import MapHash
from openra.services.map_database_service import (MapDatabaseService, ExceptionMapAlreadyExists,
                                                  ExceptionMapMetadataMissing)
from openra.tests.factories import UserFactory
from openra.tests.helpers import UniqueHashGenerator


class TestServiceMapDatabaseService(TestCase):

    def get_unique_hash(self):
        """Generate a unique 40-character hash for testing"""
        return UniqueHashGenerator.get_unique_hash()

    def setUp(self):
        self.service = MapDatabaseService()
        self.user = UserFactory()

        # Sample metadata that includes all required fields
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

    def test_save_map_record_creates_map_successfully(self):
        # Setup
        map_hash = MapHash(self.get_unique_hash())

        # Execute
        result = self.service.save_map_record(
            map_hash=map_hash,
            metadata=self.valid_metadata,
            user=self.user,
            parser='release-20231010',
            description='Test description',
            policy=self.valid_policy,
            revision=1,
            previous_revision_id=0
        )

        # Assert
        self.assertIsInstance(result, Maps)
        self.assertEqual(result.map_hash, map_hash.map_hash)
        self.assertEqual(result.title, 'Test Map')
        self.assertEqual(result.author, 'Test Author')
        self.assertEqual(result.user, self.user)
        self.assertEqual(result.parser, 'release-20231010')
        self.assertEqual(result.info, 'Test description')
        self.assertEqual(result.revision, 1)
        self.assertEqual(result.pre_rev, 0)
        self.assertEqual(result.next_rev, 0)
        self.assertTrue(result.policy_cc)
        self.assertFalse(result.policy_commercial)
        self.assertEqual(result.policy_adaptations, 'yes')
        self.assertTrue(result.downloading)
        self.assertFalse(result.requires_upgrade)  # ra is a known mod
        self.assertFalse(result.advanced_map)  # starts as False
        self.assertEqual(result.base64_rules, '')  # starts empty

        # Check database persistence
        saved_map = Maps.objects.get(id=result.id)
        self.assertEqual(saved_map.map_hash, map_hash.map_hash)

    def test_save_map_record_sets_requires_upgrade_for_unknown_mod(self):
        # Setup - use an unknown mod
        metadata = self.valid_metadata.copy()
        metadata['game_mod'] = 'unknown_mod'
        map_hash = MapHash(self.get_unique_hash())

        # Execute
        result = self.service.save_map_record(
            map_hash=map_hash,
            metadata=metadata,
            user=self.user,
            parser='release-20231010',
            description='Test description',
            policy=self.valid_policy
        )

        # Assert
        self.assertTrue(result.requires_upgrade)  # unknown mod should require upgrade

    def test_save_map_record_links_to_previous_revision(self):
        # Setup - create a previous revision
        previous_map = Maps.objects.create(
            map_hash=self.get_unique_hash(),
            title='Previous Map',
            author='Test Author',
            user=self.user,
            parser='release-20231010',
            revision=1,
            pre_rev=0,
            next_rev=0,
            posted=timezone.now()
        )

        map_hash = MapHash(self.get_unique_hash())

        # Execute
        result = self.service.save_map_record(
            map_hash=map_hash,
            metadata=self.valid_metadata,
            user=self.user,
            parser='release-20231010',
            description='Test description',
            policy=self.valid_policy,
            revision=2,
            previous_revision_id=previous_map.id
        )

        # Assert
        self.assertEqual(result.revision, 2)
        self.assertEqual(result.pre_rev, previous_map.id)

        # Check that previous revision was updated
        previous_map.refresh_from_db()
        self.assertEqual(previous_map.next_rev, result.id)

    def test_save_map_record_throws_exception_on_duplicate_hash(self):
        # Setup - create existing map with same hash
        existing_hash = self.get_unique_hash()
        Maps.objects.create(
            map_hash=existing_hash,
            title='Existing Map',
            author='Existing Author',
            user=self.user,
            parser='release-20231010',
            posted=timezone.now()
        )

        map_hash = MapHash(existing_hash)

        # Execute & Assert
        with self.assertRaises(ExceptionMapAlreadyExists) as context:
            self.service.save_map_record(
                map_hash=map_hash,
                metadata=self.valid_metadata,
                user=self.user,
                parser='release-20231010',
                description='Test description',
                policy=self.valid_policy
            )

        # Check exception details
        exception = context.exception
        self.assertEqual(exception.message, "Map has already been uploaded")
        self.assertIn(f'map_hash: {existing_hash}', exception.detail)

    def test_save_map_record_throws_exception_on_missing_metadata(self):
        # Setup - remove required field
        incomplete_metadata = self.valid_metadata.copy()
        del incomplete_metadata['title']

        map_hash = MapHash(self.get_unique_hash())

        # Execute & Assert
        with self.assertRaises(ExceptionMapMetadataMissing) as context:
            self.service.save_map_record(
                map_hash=map_hash,
                metadata=incomplete_metadata,
                user=self.user,
                parser='release-20231010',
                description='Test description',
                policy=self.valid_policy
            )

        # Check exception details
        exception = context.exception
        self.assertEqual(exception.message, "Map metadata missing required field: title")
        self.assertIn('field: title', exception.detail)

    def test_save_map_record_validates_all_required_fields(self):
        # Test each required field individually
        required_fields = ['title', 'author', 'categories', 'players', 'game_mod',
                           'width', 'height', 'bounds', 'mapformat', 'spawnpoints',
                           'tileset', 'base64_players', 'lua']

        for field in required_fields:
            # Use unique hash for each test to avoid conflicts
            map_hash = MapHash(self.get_unique_hash())
            incomplete_metadata = self.valid_metadata.copy()
            del incomplete_metadata[field]

            with self.assertRaises(ExceptionMapMetadataMissing) as context:
                self.service.save_map_record(
                    map_hash=map_hash,
                    metadata=incomplete_metadata,
                    user=self.user,
                    parser='release-20231010',
                    description='Test description',
                    policy=self.valid_policy
                )

            exception = context.exception
            self.assertEqual(exception.message, f"Map metadata missing required field: {field}")

    def test_update_map_advanced_status_updates_correctly(self):
        # Setup - create a map
        test_map = Maps.objects.create(
            map_hash=self.get_unique_hash(),
            title='Test Map',
            author='Test Author',
            user=self.user,
            parser='release-20231010',
            advanced_map=False,
            base64_rules='',
            posted=timezone.now()
        )

        # Execute
        self.service.update_map_advanced_status(
            map_id=test_map.id,
            is_advanced=True,
            base64_rules='dGVzdCBydWxlcw=='
        )

        # Assert
        test_map.refresh_from_db()
        self.assertTrue(test_map.advanced_map)
        self.assertEqual(test_map.base64_rules, 'dGVzdCBydWxlcw==')

    def test_update_map_advanced_status_without_rules(self):
        # Setup - create a map
        test_map = Maps.objects.create(
            map_hash=self.get_unique_hash(),
            title='Test Map',
            author='Test Author',
            user=self.user,
            parser='release-20231010',
            advanced_map=False,
            base64_rules='old_rules',
            posted=timezone.now()
        )

        # Execute - update without providing base64_rules
        self.service.update_map_advanced_status(
            map_id=test_map.id,
            is_advanced=True
        )

        # Assert
        test_map.refresh_from_db()
        self.assertTrue(test_map.advanced_map)
        self.assertEqual(test_map.base64_rules, '')  # Should default to empty string

    def test_update_map_upgrade_status_updates_correctly(self):
        # Setup - create a map
        test_map = Maps.objects.create(
            map_hash=self.get_unique_hash(),
            title='Test Map',
            author='Test Author',
            user=self.user,
            parser='release-20231010',
            requires_upgrade=True,
            posted=timezone.now()
        )

        # Execute
        self.service.update_map_upgrade_status(
            map_id=test_map.id,
            requires_upgrade=False
        )

        # Assert
        test_map.refresh_from_db()
        self.assertFalse(test_map.requires_upgrade)

    def test_is_known_mod_recognizes_supported_mods(self):
        # Test known mods
        known_mods = ['ra', 'cnc', 'd2k', 'ts', 'RA', 'CNC', 'D2K', 'TS']  # Test case insensitive

        for mod in known_mods:
            self.assertTrue(self.service._is_known_mod(mod))

    def test_is_known_mod_rejects_unknown_mods(self):
        # Test unknown mods
        unknown_mods = ['unknown', 'custom_mod', '', None]

        for mod in unknown_mods:
            if mod is not None:  # _is_known_mod expects string
                self.assertFalse(self.service._is_known_mod(mod))
