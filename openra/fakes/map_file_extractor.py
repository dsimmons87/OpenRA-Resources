from fs.tempfs import TempFS
from openra.classes.file_location import FileLocation
from openra.classes.extracted_map import ExtractedMap


class FakeMapFileExtractor:
    """Fake MapFileExtractor for testing."""

    def __init__(self):
        """Initialize fake extractor."""
        self.should_fail = False
        self.metadata = {
            'title': 'Test Map',
            'author': 'Test Author',
            'game_mod': 'ra',
            'tileset': 'desert',
            'players': '2',
            'map_type': 'Skirmish',
            'width': 64,
            'height': 64,
            'bounds': '0,0,64,64',
            'mapformat': '11',
            'categories': 'conquest'
        }

    def open_in_place(self, file_location: FileLocation):
        """Extract map file in place."""
        if self.should_fail:
            raise Exception("Fake extraction failed")

        # Create a temporary filesystem for the extracted content
        temp_fs = TempFS()

        # Create fake map.yaml
        temp_fs.makedirs('content')
        temp_fs.touch('content/map.yaml')
        temp_fs.writetext('content/map.yaml', 'fake: map content')

        extracted_location = FileLocation(
            temp_fs,
            '',
            'content'
        )

        return FakeExtractedMap(extracted_location, self.metadata)


class FakeExtractedMap(ExtractedMap):
    """Fake ExtractedMap for testing."""

    def __init__(self, location: FileLocation, metadata: dict):
        super().__init__(location)
        self._metadata = metadata

    def parse_metadata(self):
        """Return fake metadata."""
        return self._metadata
