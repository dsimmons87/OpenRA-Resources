
import base64
from openra.classes.file_location import FileLocation


class ExtractedMap:

    location: FileLocation

    def __init__(self, location: FileLocation):
        self.location = location

    def parse_metadata(self):
        # TODO: Replace this DIY parsing with a utility command that returns JSON
        # TODO: Will need a migration to remove the quote-doubling from title and author
        metadata = {
            'mapformat': 0,
            'lua': False,
            'players': 0,
            'title': '',
            'author': '',
            'tileset': '',
            'categories': '',
            'width': 0,
            'height': 0,
            'bounds': '0,0,0,0',
            'base64_players': ''
        }

        yaml_data = ""
        for name in self.location.fs.listdir('/'):
            if name == "map.yaml":
                yaml_data = self.location.fs.readtext(name)
            if name.endswith('.lua'):
                metadata['lua'] = True

        if not yaml_data:
            return None

        in_players_node = False
        in_actors_node = False
        in_spawn_node = False

        spawn_locations = []
        players_nodes = ''

        for line in yaml_data.split('\n'):
            # Count starting indent
            space_indent = 0
            tab_indent = 0
            for char in line:
                if char not in [' ', '\t']:
                    break
                if char == '\t':
                    tab_indent += 1
                else:
                    space_indent += 1
            indent = int(tab_indent + space_indent // 4)

            if in_players_node and indent == 0:
                in_players_node = False
            if in_actors_node and indent == 0:
                in_actors_node = False
            if in_spawn_node and indent < 2:
                in_spawn_node = False

            if in_players_node:
                players_nodes += '\t' * (indent - 1) + line.strip() + '\n'

            split_index = line.find(':')
            if split_index < 0:
                continue

            key = line[:split_index].strip()
            value = line[split_index + 1:].strip()
            if key == 'Title':
                metadata['title'] = value.replace("'", "''")
            elif key == 'RequiresMod':
                metadata['game_mod'] = value.lower()
            elif key == 'Author':
                metadata['author'] = value.replace("'", "''")
            elif key == 'Tileset':
                metadata['tileset'] = value
            elif key == 'Categories':
                categories = []
                for category_item in value.split(','):
                    categories.append(category_item.strip())
                metadata['categories'] = categories
            elif key == 'MapSize':
                size = value.split(',')
                metadata['width'] = size[0]
                metadata['height'] = size[1]
            elif key == 'Bounds':
                metadata['bounds'] = value
            elif key == 'MapFormat':
                metadata['mapformat'] = int(value)
            elif key == 'Actors':
                in_actors_node = True
            elif in_actors_node and value.lower() == 'mpspawn':
                in_spawn_node = True
            elif in_spawn_node and key == "Location":
                spawn_locations.append(value)

            elif key == 'Players':
                in_players_node = True
            elif in_players_node and key == 'Playable':
                if value.lower() in ['true', 'on', 'yes', 'y']:
                    metadata['players'] += 1

        metadata['spawnpoints'] = ', '.join(spawn_locations)

        if players_nodes:
            metadata['base64_players'] = base64.b64encode(players_nodes.encode()).decode()

        return metadata

