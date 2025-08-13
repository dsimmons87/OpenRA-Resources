from django.contrib.auth.models import User
from openra.models import Maps
from openra.classes.file_location import FileLocation
from openra.classes.extracted_map import ExtractedMap
from openra.classes.map_hash import MapHash
from openra.classes.exceptions import ExceptionBase
from openra.services.map_database_service import MapDatabaseService
from openra.services.map_file_repository import MapFileRepository
from openra.services.utility.map_hash import MapHashCommand, MapHashTranslator
from openra.services.docker import Docker


class MapUploadOrchestrator:

    def __init__(self,
                 map_database_service: MapDatabaseService,
                 map_file_repository: MapFileRepository,
                 map_hash_command: MapHashCommand,
                 map_hash_translator: MapHashTranslator,
                 docker: Docker):
        self.map_database_service = map_database_service
        self.map_file_repository = map_file_repository
        self.map_hash_command = map_hash_command
        self.map_hash_translator = map_hash_translator
        self.docker = docker

    def upload_map(self,
                   map_file_location: FileLocation,
                   extracted_map: ExtractedMap,
                   user: User,
                   parser: str,
                   description: str,
                   policy: dict,
                   revision: int = 1,
                   previous_revision_id: int = 0) -> Maps:
        """
        Orchestrate the complete map upload process.
        Returns the created Maps model instance.
        """

        # Step 1: Calculate map hash
        hash_output = self.map_hash_command.run_command(self.docker)
        map_hash = self.map_hash_translator.translate(hash_output)

        # Step 2: Parse and validate metadata
        metadata = extracted_map.parse_metadata()
        if not metadata:
            raise ExceptionMapUploadMetadataInvalid()

        # Step 3: Save to database first (this will validate and check for duplicates)
        map_record = self.map_database_service.save_map_record(
            map_hash=map_hash,
            metadata=metadata,
            user=user,
            parser=parser,
            description=description,
            policy=policy,
            revision=revision,
            previous_revision_id=previous_revision_id
        )

        # Step 4: Store files to filesystem
        try:
            self.map_file_repository.store_map(
                map_id=map_record.id,
                map_file_location=map_file_location,
                extracted_map_location=extracted_map.location
            )
        except Exception as e:
            # If file storage fails, we need to clean up the database record
            map_record.delete()
            raise ExceptionMapUploadFileStorageFailed(str(e))

        # TODO: Step 5: Analyze rules and update advanced status
        # This would use a MapRulesAnalysisService when implemented

        # TODO: Step 6: Run linting and update upgrade status
        # This would use a MapLintingService when implemented

        return map_record


class ExceptionMapUploadMetadataInvalid(ExceptionBase):
    def __init__(self):
        super().__init__()
        self.message = "Unable to parse map metadata"


class ExceptionMapUploadFileStorageFailed(ExceptionBase):
    def __init__(self, error: str):
        super().__init__()
        self.message = "Map upload failed during file storage"
        self.detail.append('error: ' + error)
