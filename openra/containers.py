from dependency_injector import containers, providers
from fs.osfs import OSFS
from openra import settings
from os import path
import docker
from openra.services.docker import Docker
from github import Github as GithubClient
from openra.services.engine_file_repository import EngineFileRepository
from openra.services.file_downloader import FileDownloader
from openra.services.github import Github
from openra.services.log import Log
from openra.services.map_file_extractor import MapFileExtractor
from openra.services.map_file_repository import MapFileRepository
from openra.services.map_search import MapSearch
from openra.services.screenshot_repository import ScreenshotRepository
from openra.services.uploaded_file_importer import UploadedFileImporter
from openra.services.openra_master import OpenraMaster
from openra.services.utility import Utility
from openra.services.map_database_service import MapDatabaseService
from openra.services.map_upload_orchestrator import MapUploadOrchestrator
from openra.services.utility.map_hash import MapHashCommand, MapHashTranslator


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    log = providers.Singleton(
        Log
    )

    data_fs = providers.Singleton(
        OSFS,
        path.join(settings.BASE_DIR, 'openra', 'data')
    )

    docker = providers.Singleton(
        Docker,
        lambda: docker.from_env()
    )

    github = providers.Singleton(
        Github,
        providers.Callable(
            GithubClient,
            settings.GITHUB_API_KEY
        )
    )

    uploaded_file_importer = providers.Singleton(
        UploadedFileImporter
    )

    screenshot_repository = providers.Singleton(
        ScreenshotRepository
    )

    engine_file_repository = providers.Singleton(
        EngineFileRepository,
        data_fs=data_fs,
        docker=docker
    )

    map_file_repository = providers.Singleton(
        MapFileRepository,
        data_fs=data_fs
    )

    map_file_extractor = providers.Singleton(
        MapFileExtractor
    )

    file_downloader = providers.Singleton(
        FileDownloader
    )

    utility = providers.Singleton(
        Utility
    )

    map_search = providers.Singleton(
        MapSearch
    )

    openra_master = providers.Singleton(
        OpenraMaster
    )

    # Map database service
    map_database_service = providers.Singleton(
        MapDatabaseService
    )

    # Map upload orchestrator
    map_upload_orchestrator = providers.Singleton(
        MapUploadOrchestrator,
        map_database_service=map_database_service,
        map_file_repository=map_file_repository,
        engine_file_repository=engine_file_repository,
        docker=docker
    )


container = Container()
container.config.from_dict(settings.__dict__)
