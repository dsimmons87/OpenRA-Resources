from fs.zipfs import ZipFS
from openra.classes.extracted_map import ExtractedMap
from openra.classes.file_location import FileLocation


class MapFileExtractor:

    def open_in_place(self, oramap: FileLocation):
        zip_fs = ZipFS(oramap.get_os_path())
        # TODO check this works
        return ExtractedMap(
            FileLocation(
                zip_fs,
                '/',
                '',
            )
        )
