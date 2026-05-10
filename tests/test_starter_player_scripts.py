import json
import shutil
import tempfile
import unittest
from pathlib import Path

from filesystem import FileSystem
from lib import process_instructions
from rbx_dom import Instance, WeakDom


class TestStarterPlayerScriptsProject(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="rbxlx-to-rojo-starter-player-"))

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_starter_player_script_containers_keep_their_classes(self):
        root = Instance("DataModel", "DataModel", "root")
        dom = WeakDom(root)

        starter_player = Instance("StarterPlayer", "StarterPlayer", "starter_player")
        starter_player.properties["Name"] = "StarterPlayer"
        dom.insert(root.referent, starter_player)

        player_scripts = Instance("StarterPlayerScripts", "StarterPlayerScripts", "player_scripts")
        player_scripts.properties["Name"] = "StarterPlayerScripts"
        dom.insert(starter_player.referent, player_scripts)

        character_scripts = Instance("StarterCharacterScripts", "StarterCharacterScripts", "character_scripts")
        character_scripts.properties["Name"] = "StarterCharacterScripts"
        dom.insert(starter_player.referent, character_scripts)

        player_local_script = Instance("LocalScript", "PlayerClient", "player_client")
        player_local_script.properties["Name"] = "PlayerClient"
        player_local_script.properties["Source"] = "print('player')"
        dom.insert(player_scripts.referent, player_local_script)

        character_local_script = Instance("LocalScript", "CharacterClient", "character_client")
        character_local_script.properties["Name"] = "CharacterClient"
        character_local_script.properties["Source"] = "print('character')"
        dom.insert(character_scripts.referent, character_local_script)

        filesystem = FileSystem.from_root(self.temp_dir / "output")
        process_instructions(dom, filesystem)

        project = json.loads((self.temp_dir / "output" / "default.project.json").read_text(encoding="utf-8"))
        starter_player_tree = project["tree"]["StarterPlayer"]

        self.assertEqual(
            starter_player_tree["StarterPlayerScripts"]["$className"],
            "StarterPlayerScripts",
        )
        self.assertEqual(
            starter_player_tree["StarterCharacterScripts"]["$className"],
            "StarterCharacterScripts",
        )


if __name__ == "__main__":
    unittest.main()
