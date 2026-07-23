import tempfile
import unittest
from pathlib import Path

from aider.io import InputOutput
from aider.repomap import RepoMap
from aider.repomap_loader import load_repo_map_class


class TestRepoMapLoader(unittest.TestCase):
    def test_load_class_from_relative_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            module_path = Path(temp_dir) / "custom_map.py"
            module_path.write_text(
                "from aider.repomap import RepoMap\n"
                "\n"
                "class CustomRepoMap(RepoMap):\n"
                "    pass\n"
            )

            repo_map_class = load_repo_map_class(
                "custom_map.py:CustomRepoMap", root=temp_dir
            )

            self.assertTrue(issubclass(repo_map_class, RepoMap))
            self.assertEqual(repo_map_class.__name__, "CustomRepoMap")

    def test_load_class_from_module(self):
        repo_map_class = load_repo_map_class("aider.repomap:RepoMap")

        self.assertIs(repo_map_class, RepoMap)

    def test_load_module_relative_to_root(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            module_path = Path(temp_dir) / "root_map.py"
            module_path.write_text(
                "from aider.repomap import RepoMap\n"
                "\n"
                "class RootRepoMap(RepoMap):\n"
                "    pass\n"
            )

            repo_map_class = load_repo_map_class(
                "root_map:RootRepoMap", root=temp_dir
            )

            self.assertEqual(repo_map_class.__name__, "RootRepoMap")

    def test_reject_invalid_spec(self):
        with self.assertRaisesRegex(ValueError, "MODULE:CLASS"):
            load_repo_map_class("custom_map.py")

    def test_reject_missing_file(self):
        with self.assertRaisesRegex(ValueError, "does not exist"):
            load_repo_map_class("missing.py:CustomRepoMap")

    def test_reject_missing_class(self):
        with self.assertRaisesRegex(ValueError, "was not found"):
            load_repo_map_class("aider.repomap:MissingRepoMap")

    def test_reject_non_repo_map_class(self):
        with self.assertRaisesRegex(ValueError, "must inherit"):
            load_repo_map_class("pathlib:Path")

    def test_custom_classes_use_separate_tag_caches(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_file = root / "source.py"
            source_file.write_text("value = 1\n")

            for module_name, tag_name in (("first_map", "first"), ("second_map", "second")):
                (root / f"{module_name}.py").write_text(
                    "from aider.repomap import RepoMap, Tag\n"
                    "\n"
                    "class CustomRepoMap(RepoMap):\n"
                    "    def get_tags_raw(self, fname, rel_fname):\n"
                    f"        yield Tag(rel_fname, fname, 0, {tag_name!r}, 'def')\n"
                )

            first_class = load_repo_map_class(
                "first_map.py:CustomRepoMap", root=temp_dir
            )
            second_class = load_repo_map_class(
                "second_map.py:CustomRepoMap", root=temp_dir
            )
            first_map = first_class(root=temp_dir, io=InputOutput())
            second_map = second_class(root=temp_dir, io=InputOutput())

            try:
                first_tags = first_map.get_tags(str(source_file), source_file.name)
                second_tags = second_map.get_tags(str(source_file), source_file.name)
            finally:
                first_map.TAGS_CACHE.close()
                second_map.TAGS_CACHE.close()

            self.assertEqual([tag.name for tag in first_tags], ["first"])
            self.assertEqual([tag.name for tag in second_tags], ["second"])
