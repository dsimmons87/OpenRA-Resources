from django.contrib.auth.models import User
from django.utils import timezone
from openra.models import Maps
from openra.classes.exceptions import ExceptionBase
from openra.classes.map_hash import MapHash


class MapDatabaseService:

    def save_map_record(self,
                        map_hash: MapHash,
                        metadata: dict,
                        user: User,
                        parser: str,
                        description: str,
                        policy: dict,
                        revision: int = 1,
                        previous_revision_id: int = 0) -> Maps:
        """
        Save a map record to the database.
        Returns the created Maps model instance.
        """

        # Check for duplicates
        if Maps.objects.filter(map_hash=map_hash.map_hash).exists():
            raise ExceptionMapAlreadyExists(map_hash.map_hash)

        # Validate required metadata fields
        required_fields = ['title', 'author', 'categories', 'players', 'game_mod',
                           'width', 'height', 'bounds', 'mapformat', 'spawnpoints',
                           'tileset', 'base64_players', 'lua']

        for field in required_fields:
            if field not in metadata:
                raise ExceptionMapMetadataMissing(field)

        # Create database record
        map_item = Maps(
            map_hash=map_hash.map_hash,
            revision=revision,
            pre_rev=previous_revision_id,
            next_rev=0,
            posted=timezone.now(),
            viewed=0,
            base64_rules='',  # TODO: Will be set by rules extraction service
            parser=parser,
            user=user,
            info=description,
            downloading=True,
            requires_upgrade=not self._is_known_mod(metadata['game_mod']),
            advanced_map=False,  # TODO: Will be set by rules analysis service
            policy_cc=policy['cc'],
            policy_commercial=policy['commercial'],
            policy_adaptations=policy['adaptations'],
            description='',  # Obsolete field
            map_type='',     # Obsolete field
            shellmap=False,  # Obsolete field
            legacy_map=False,  # Obsolete field
            **{k: v for k, v in metadata.items() if k in required_fields}
        )
        map_item.save()

        # Link to previous revision if applicable
        if previous_revision_id:
            previous_item = Maps.objects.get(id=previous_revision_id)
            previous_item.next_rev = map_item.id
            previous_item.save()

        return map_item

    def update_map_advanced_status(self, map_id: int, is_advanced: bool, base64_rules: str = ''):
        """Update a map's advanced status and rules after analysis"""
        Maps.objects.filter(id=map_id).update(
            advanced_map=is_advanced,
            base64_rules=base64_rules
        )

    def update_map_upgrade_status(self, map_id: int, requires_upgrade: bool):
        """Update a map's upgrade requirement status after validation"""
        Maps.objects.filter(id=map_id).update(requires_upgrade=requires_upgrade)

    def _is_known_mod(self, game_mod: str) -> bool:
        """Check if this is a known mod that we can process"""
        return game_mod.lower() in ['ra', 'cnc', 'd2k', 'ts']


class ExceptionMapAlreadyExists(ExceptionBase):
    def __init__(self, map_hash: str):
        super().__init__()
        self.message = "Map has already been uploaded"
        self.detail.append(f'map_hash: {map_hash}')


class ExceptionMapMetadataMissing(ExceptionBase):
    def __init__(self, field: str):
        super().__init__()
        self.message = f"Map metadata missing required field: {field}"
        self.detail.append(f'field: {field}')
