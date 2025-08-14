from django.contrib.auth.models import User
from openra.models import Maps
from openra.classes.file_location import FileLocation
from openra.classes.extracted_map import ExtractedMap
from openra.tests.factories import MapsFactory


class FakeMapUploadOrchestrator:
    """Fake MapUploadOrchestrator for testing that doesn't require Docker."""

    def __init__(self, map_database_service=None, map_file_repository=None,
                 engine_file_repository=None, docker=None):
        """Initialize fake orchestrator."""
        self.should_fail = False
        self.error_message = ""
        self.created_map = None
        self.custom_exception = None

    def upload_map(self,
                   map_file_location: FileLocation,
                   extracted_map: ExtractedMap,
                   user: User,
                   parser: str,
                   description: str,
                   policy: dict,
                   revision: int = 1,
                   previous_revision_id: int = 0) -> Maps:
        """Fake upload that returns a mock Maps instance."""
        if self.custom_exception:
            raise self.custom_exception
        
        if self.should_fail:
            from openra.services.map_upload_orchestrator import ExceptionMapUploadMetadataInvalid
            raise ExceptionMapUploadMetadataInvalid()

        # Create a fake map using the factory
        fake_map = MapsFactory(
            user=user,
            parser=parser,
            info=description,
            revision=revision,
            pre_rev=previous_revision_id,
            policy_cc=policy.get('cc', False),
            policy_commercial=policy.get('commercial', False),
            policy_adaptations=policy.get('adaptations', '')
        )

        self.created_map = fake_map
        return fake_map
    
    def set_upload_map_exception(self, exception: Exception):
        """Set a custom exception to be raised by upload_map."""
        self.custom_exception = exception
