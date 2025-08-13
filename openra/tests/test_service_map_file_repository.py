from unittest import TestCase
from unittest.mock import MagicMock, Mock
from fs.memoryfs import MemoryFS

from fs.tempfs import TempFS
from openra.classes.file_location import FileLocation
from openra.services.map_file_repository import (ExceptionMapContentFolderNotFound, ExceptionMapFolderNotFound,
                                                 ExceptionOramapNotFound, ExceptionMapFileStorageFailed,
                                                 ExceptionMapContentStorageFailed, MapFileRepository)


class TestServiceMapFileRepository(TestCase):

    def test_get_oramap_path_returns_map_oramap_path(self):
        fs = TempFS()
        fs.makedirs('maps/1')
        fs.touch('maps/1/mymap.oramap')

        map_file_repository = MapFileRepository(
            data_fs=fs,
        )

        location = map_file_repository.get_oramap_path(1)

        self.assertIsInstance(
            location,
            FileLocation
        )

        self.assertEquals(
            location.fs,
            fs
        )

        self.assertEquals(
            location.path,
            'maps/1',
        )

        self.assertEquals(
            location.file,
            'mymap.oramap',
        )

    def test_get_oramap_path_throws_exception_if_folder_doesnt_exist(self):
        fs = TempFS()

        map_file_repository = MapFileRepository(
            data_fs=fs,
        )

        self.assertRaises(
            ExceptionMapFolderNotFound,
            map_file_repository.get_oramap_path,
            1
        )

    def test_get_oramap_path_throws_exception_if_no_oramap_exists(self):
        fs = TempFS()
        fs.makedirs('maps/1')
        fs.touch('maps/1/mymap.notoramap')

        map_file_repository = MapFileRepository(
            data_fs=fs,
        )

        self.assertRaises(
            ExceptionOramapNotFound,
            map_file_repository.get_oramap_path,
            1
        )

    def test_get_lua_paths_returns_map_lua_paths(self):
        fs = TempFS()
        fs.makedirs('maps/1/content')
        fs.touch('maps/1/mymap.oramap')
        fs.touch('maps/1/content/mylua1.lua')
        fs.touch('maps/1/content/mylua2.lua')
        fs.touch('maps/1/content/somefile.yaml')

        map_file_repository = MapFileRepository(
            data_fs=fs,
        )

        locations = map_file_repository.get_lua_paths(1)

        self.assertEquals(2, len(locations))

        self.assertIsInstance(
            locations[0],
            FileLocation
        )

        self.assertEquals(
            locations[0].fs,
            fs
        )

        self.assertEquals(
            locations[0].path,
            'maps/1/content',
        )

        self.assertEquals(
            locations[0].file,
            'mylua1.lua',
        )

        self.assertIsInstance(
            locations[1],
            FileLocation
        )

        self.assertEquals(
            locations[1].fs,
            fs
        )

        self.assertEquals(
            locations[1].path,
            'maps/1/content',
        )

        self.assertEquals(
            locations[1].file,
            'mylua2.lua',
        )

    def test_get_lua_paths_throws_exception_if_folder_doesnt_exist(self):
        fs = TempFS()

        map_file_repository = MapFileRepository(
            data_fs=fs,
        )

        self.assertRaises(
            ExceptionMapContentFolderNotFound,
            map_file_repository.get_lua_paths,
            1
        )

    def test_store_map_creates_directories_and_stores_files(self):
        # Setup: Create source filesystems with test data
        source_fs = TempFS()
        extracted_fs = TempFS()
        target_fs = TempFS()

        # Create a mock map file
        source_fs.writetext('test.oramap', 'mock oramap content')
        map_file_location = FileLocation(source_fs, '', 'test.oramap')

        # Create mock extracted content
        extracted_fs.writetext('map.yaml', 'mock yaml content')
        extracted_fs.writetext('script.lua', 'mock lua content')
        extracted_map_location = FileLocation(extracted_fs, '/', '')

        map_file_repository = MapFileRepository(data_fs=target_fs)

        # Execute: Store the map
        result = map_file_repository.store_map(123, map_file_location, extracted_map_location)

        # Assert: Check that directories were created
        self.assertTrue(target_fs.exists('maps/123'))
        self.assertTrue(target_fs.exists('maps/123/content'))

        # Assert: Check that files were copied
        self.assertTrue(target_fs.exists('maps/123/test.oramap'))
        self.assertTrue(target_fs.exists('maps/123/content/map.yaml'))
        self.assertTrue(target_fs.exists('maps/123/content/script.lua'))

        # Assert: Check file contents
        self.assertEqual(target_fs.readtext('maps/123/test.oramap'), 'mock oramap content')
        self.assertEqual(target_fs.readtext('maps/123/content/map.yaml'), 'mock yaml content')
        self.assertEqual(target_fs.readtext('maps/123/content/script.lua'), 'mock lua content')

        # Assert: Check return value
        self.assertIsInstance(result, FileLocation)
        self.assertEqual(result.fs, target_fs)
        self.assertEqual(result.path, 'maps/123')
        self.assertEqual(result.file, 'test.oramap')

    def test_store_map_uses_default_filename_when_none_provided(self):
        source_fs = TempFS()
        extracted_fs = TempFS()
        target_fs = TempFS()

        # Create map file
        source_fs.writetext('somefile.oramap', 'content')
        map_file_location = FileLocation(source_fs, '', 'somefile.oramap')

        # Mock the file attribute to return None/empty to test fallback
        original_file = map_file_location.file
        map_file_location.file = None

        # We need to override get_fs_path to still work with the original file
        def mock_get_fs_path():
            return original_file
        map_file_location.get_fs_path = mock_get_fs_path

        extracted_map_location = FileLocation(extracted_fs, '/', '')

        map_file_repository = MapFileRepository(data_fs=target_fs)

        result = map_file_repository.store_map(456, map_file_location, extracted_map_location)

        # Should use default filename
        self.assertTrue(target_fs.exists('maps/456/map.oramap'))
        self.assertEqual(result.file, 'map.oramap')

    def test_store_map_throws_exception_on_file_copy_failure(self):
        # Setup: Create source filesystems
        source_fs = TempFS()
        extracted_fs = TempFS()
        target_fs = TempFS()

        # Create a non-existent file to force copy failure
        map_file_location = FileLocation(source_fs, '', 'nonexistent.oramap')
        extracted_map_location = FileLocation(extracted_fs, '/', '')

        map_file_repository = MapFileRepository(data_fs=target_fs)

        # This should fail because the source file doesn't exist
        with self.assertRaises(ExceptionMapFileStorageFailed) as context:
            map_file_repository.store_map(789, map_file_location, extracted_map_location)

        # Check exception details
        exception = context.exception
        self.assertEqual(exception.message, "Failed to store map file")
        self.assertIn('map: 789', exception.detail)

    def test_store_map_throws_exception_on_content_copy_failure(self):
        # Setup filesystems
        source_fs = TempFS()
        target_fs = TempFS()

        # Create a failing extracted filesystem
        extracted_fs = Mock()

        source_fs.writetext('test.oramap', 'content')
        map_file_location = FileLocation(source_fs, '', 'test.oramap')
        extracted_map_location = FileLocation(extracted_fs, '/', '')

        map_file_repository = MapFileRepository(data_fs=target_fs)

        # We need to mock the copy module to make copy_dir fail but copy_file succeed
        import unittest.mock
        with unittest.mock.patch('fs.copy.copy_file') as mock_copy_file:
            with unittest.mock.patch('fs.copy.copy_dir') as mock_copy_dir:
                mock_copy_file.return_value = None  # copy_file succeeds
                mock_copy_dir.side_effect = Exception("Content copy failed")  # copy_dir fails

                with self.assertRaises(ExceptionMapContentStorageFailed) as context:
                    map_file_repository.store_map(999, map_file_location, extracted_map_location)

                # Check exception details
                exception = context.exception
                self.assertEqual(exception.message, "Failed to store map content")
                self.assertIn('map: 999', exception.detail)
