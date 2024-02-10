import json
import os

class CharacterManager:
    def __init__(self, characters_dir=None):
        if characters_dir is None:
            # Assumes the current working directory is the root of your project
            self.characters_dir = os.path.join('src', 'characters')
        else:
            self.characters_dir = characters_dir
        
        if not os.path.exists(self.characters_dir):
            os.makedirs(self.characters_dir)

    def load_character_config(self, bot_name):
        """
        Load character configuration from a JSON file.
        If the file doesn't exist, return a default configuration.
        """
        file_path = self._get_character_file_path(bot_name)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                return json.load(file)
        else:
            return self._default_config()

    def save_character_config(self, bot_name, config):
        """
        Save the character configuration to a JSON file.
        """
        file_path = self._get_character_file_path(bot_name)
        with open(file_path, 'w') as file:
            json.dump(config, file, indent=4)

    def _get_character_file_path(self, bot_name):
        """
        Helper method to generate the file path for a character's config file.
        """
        return os.path.join(self.characters_dir, f'{bot_name}.json')

    def _default_config(self):
        """
        Returns a default character configuration.
        This can be expanded based on what default values you need.
        """
        return {
            'system_message': 'You are a character in a roleplay.',
            # Add more default settings as needed
        }
