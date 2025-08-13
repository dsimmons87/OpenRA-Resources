from fs.tempfs import TempFS
from openra.classes.file_location import FileLocation


class FakeUploadedFileImporter:
    """Fake UploadedFileImporter for testing."""

    def __init__(self):
        """Initialize fake importer."""
        self.should_fail = False

    def import_file(self, uploaded_file, filename):
        """Import uploaded file to temporary location."""
        if self.should_fail:
            raise Exception("Fake import failed")

        # Create a temporary file system and fake file
        temp_fs = TempFS()
        temp_fs.touch(filename)

        return FileLocation(
            temp_fs,
            '',
            filename
        )
