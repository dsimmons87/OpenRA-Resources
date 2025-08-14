class FakeDocker:
    """Fake Docker service for testing that doesn't require actual Docker connection."""

    def __init__(self, client_factory=None):
        """Initialize fake Docker service."""
        self._client_factory = client_factory

    def test_docker(self):
        """Return fake Docker test result."""
        return "Fake Docker running ok"

    def extract_appimage(self, app_image_path: str, to_dir: str):
        """Fake AppImage extraction."""
        return "Fake AppImage extracted"

    def run_utility_command(self, engine_path, command, additional_volumes=[]):
        """Fake utility command execution."""
        return "Fake utility command output"
