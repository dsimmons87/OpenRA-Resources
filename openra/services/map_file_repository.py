from dependency_injector.wiring import Provide, inject
from django.conf import os
from fs.base import FS
from openra.classes.exceptions import ExceptionBase
from openra.classes.file_location import FileLocation


class MapFileRepository:

    _data_fs: FS

    @inject
    def __init__(
        self,
        data_fs: FS = Provide['data_fs']
    ):
        self._data_fs = data_fs

    def get_oramap_path(self, map_id: int):
        path = self._get_target_path_and_throw_exception_if_doesnt_exist(map_id)

        for file in self._data_fs.filterdir(path, ['*.oramap'], None, ['*']):
            return FileLocation(
                self._data_fs,
                path,
                file.name
            )

        raise ExceptionOramapNotFound(self._data_fs, map_id, path)

    def get_lua_paths(self, map_id: int):
        path = self._get_content_path_and_throw_exception_if_doesnt_exist(map_id)

        lua_locations = []

        for file in self._data_fs.filterdir(path, ['*.lua'], None, ['*']):
            lua_locations.append(FileLocation(
                self._data_fs,
                path,
                file.name
            ))

        return lua_locations

    def _get_target_path_and_throw_exception_if_doesnt_exist(self, map_id: int):
        path = self._get_target_path(map_id)

        if not self._data_fs.exists(path):
            raise ExceptionMapFolderNotFound(self._data_fs, map_id, path)

        return path

    def _get_target_path(self, map_id: int):
        return os.path.join('maps', str(map_id))

    def _get_content_path_and_throw_exception_if_doesnt_exist(self, map_id: int):
        path = self._get_content_path(map_id)

        if not self._data_fs.exists(path):
            raise ExceptionMapContentFolderNotFound(self._data_fs, map_id, path)

        return path

    def _get_content_path(self, map_id: int):
        return os.path.join('maps', str(map_id), 'content')

    def store_map(self, map_id: int, map_file_location: FileLocation, extracted_map_location: FileLocation):
        """Store the map file and its extracted contents"""
        from fs import copy

        target_path = self._get_target_path(map_id)
        content_path = self._get_content_path(map_id)

        # Create directories if they don't exist
        if not self._data_fs.exists(target_path):
            self._data_fs.makedirs(target_path)
        if not self._data_fs.exists(content_path):
            self._data_fs.makedirs(content_path)

        # Store the original map file
        original_filename = map_file_location.file or 'map.oramap'
        target_map_path = os.path.join(target_path, original_filename)

        try:
            copy.copy_file(
                map_file_location.fs,
                map_file_location.get_fs_path(),
                self._data_fs,
                target_map_path
            )
        except Exception as e:
            raise ExceptionMapFileStorageFailed(map_id, str(e))

        # Store extracted contents - this is critical for the map to function
        try:
            copy.copy_dir(
                extracted_map_location.fs,
                extracted_map_location.path,
                self._data_fs,
                content_path
            )
        except Exception as e:
            raise ExceptionMapContentStorageFailed(map_id, str(e))

        return FileLocation(self._data_fs, target_path, original_filename)


class ExceptionMapFolderNotFound(ExceptionBase):
    def __init__(self, fs: FS, map_id: int, path: str):
        super().__init__()
        self.message = "Folder not found for map"
        self.detail.append('fs type: ' + str(type(fs)))
        self.detail.append('map: ' + str(map_id))
        self.detail.append('path: ' + path)


class ExceptionMapContentFolderNotFound(ExceptionBase):
    def __init__(self, fs: FS, map_id: int, path: str):
        super().__init__()
        self.message = "Content folder not found for map"
        self.detail.append('fs type: ' + str(type(fs)))
        self.detail.append('map: ' + str(map_id))
        self.detail.append('path: ' + path)


class ExceptionOramapNotFound(ExceptionBase):
    def __init__(self, fs: FS, map_id: int, path: str):
        super().__init__()
        self.message = "Oramap file not found for map"
        self.detail.append('fs type: ' + str(type(fs)))
        self.detail.append('map: ' + str(map_id))
        self.detail.append('path: ' + path)


class ExceptionMapFileStorageFailed(ExceptionBase):
    def __init__(self, map_id: int, error: str):
        super().__init__()
        self.message = "Failed to store map file"
        self.detail.append('map: ' + str(map_id))
        self.detail.append('error: ' + error)


class ExceptionMapContentStorageFailed(ExceptionBase):
    def __init__(self, map_id: int, error: str):
        super().__init__()
        self.message = "Failed to store map content"
        self.detail.append('map: ' + str(map_id))
        self.detail.append('error: ' + error)
