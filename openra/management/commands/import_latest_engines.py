from openra.classes.exceptions import ExceptionBase
from openra.facades import log
from typing import List
from dependency_injector.wiring import Provide, inject
from django.core.management.base import BaseCommand
from openra.containers import Container
import re
from openra.models import Engines
from openra.services.engine_file_repository import EngineFileRepository
from openra.services.file_downloader import FileDownloader

from openra.services.github import Github

class Command(BaseCommand):
    help = 'Pulls the latest engines from GitHub'

    def add_arguments(self, parser):
        parser.add_argument('release_count', type=int, nargs='?', default=1)
        pass

    def handle(self, *args, **options):
        try:
            release_count = options['release_count']
            log().info("Checking github for the last {} release(s)".format(release_count))
            engines = self._get_latest_engines(release_count)

            log().info('The following engines were discovered on github')
            for engine in engines:
                log().info(engine.mod + ' ' + engine.version + ' ' + engine.url)

            self._download_engines(engines)

            log().info('Complete')
        except ExceptionBase as exception:
            log().info('Complete')
            log.exception_obj(exception)

    @inject
    def _get_latest_engines(self, release_count=1, github:Github=Provide[Container.github]):
        playtest_regex = re.compile('^playtest-')
        engines:List[EngineInfo] = []

        for release in github.get_releases():
            tag = release.tag
            is_playtest = playtest_regex.match(tag)

            if is_playtest and len(engines) > 0:
                continue

            engines += self._get_release_engines(tag, github)

            if is_playtest:
                continue

            release_count -= 1

            if release_count == 0:
                break

        return engines

    def _get_release_engines(self, tag, github:Github):

        mod_regex = [{
            'mod': 'ra',
            'regex': re.compile('^OpenRA-Red-Alert-.*\.AppImage$')
         },{
             'mod': 'td',
             'regex': re.compile('^OpenRA-Tiberian-Dawn-.*\.AppImage$')
         },{
             'mod': 'd2k',
             'regex': re.compile('^OpenRA-Dune-2000-.*\.AppImage$')
        }]

        engines:List[EngineInfo] = []

        for asset in github.get_release_assets(tag):
            for mod in mod_regex:
                if mod['regex'].match(asset.name):
                    engines.append(
                        EngineInfo(
                            mod['mod'],
                            tag,
                            asset.url
                        )
                    )

        return engines

    @inject
    def _download_engines(self, engines,
            engine_file_repository:EngineFileRepository=Provide['engine_file_repository'],
            file_downloader:FileDownloader=Provide['file_downloader']
        ):
        for engine in engines:

            if not engine_file_repository.exists(engine.mod, engine.version):
                log().info('Downloading: ' + engine.mod + ' ' + engine.version)
                appimage_download = file_downloader.download_file(engine.url, 'appImage')

                log().info('Importing: ' + engine.mod + ' ' + engine.version)
                engine_file_repository.import_appimage(engine.mod, engine.version, appimage_download)

            if not Engines.objects.filter(
                    game_mod=engine.mod,
                    version=engine.version
                ).exists():
                log().info('Adding to database: ' + engine.mod + ' ' + engine.version)
                model = Engines(
                    game_mod=engine.mod,
                    version=engine.version
                )
                model.save()

class EngineInfo:

    mod:str
    version:str
    url:str

    def __init__(self, mod, version, url):
        self.mod = mod
        self.version = version
        self.url = url


