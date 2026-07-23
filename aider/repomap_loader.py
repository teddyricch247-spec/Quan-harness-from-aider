import hashlib
import importlib
import importlib.util
import sys
from contextlib import contextmanager
from pathlib import Path

from aider.repomap import RepoMap


@contextmanager
def _prepend_sys_path(path):
    path = str(Path(path).resolve())
    sys.path.insert(0, path)
    try:
        yield
    finally:
        try:
            sys.path.remove(path)
        except ValueError:
            pass


def _split_class_spec(spec):
    module_or_path, separator, class_name = spec.rpartition(":")
    if not separator or not module_or_path or not class_name:
        raise ValueError(
            "Invalid --map-class value. Use MODULE:CLASS or /path/to/file.py:CLASS."
        )
    return module_or_path, class_name


def _load_module_from_path(path, root=None):
    path = Path(path).expanduser()
    if not path.is_absolute():
        path = Path(root or Path.cwd()) / path
    path = path.resolve()

    if not path.is_file():
        raise ValueError(f"Repo map class file does not exist: {path}")

    module_hash = hashlib.sha256(str(path).encode()).hexdigest()[:12]
    module_name = f"_aider_repo_map_{module_hash}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Unable to load repo map class file: {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        with _prepend_sys_path(path.parent):
            spec.loader.exec_module(module)
    except Exception as err:
        sys.modules.pop(module_name, None)
        raise ValueError(f"Unable to load repo map class file {path}: {err}") from err
    return module


def load_repo_map_class(class_spec, root=None):
    """Load and validate a RepoMap subclass from a module or Python file."""
    module_or_path, class_name = _split_class_spec(class_spec)

    is_path = (
        module_or_path.endswith(".py") or "/" in module_or_path or "\\" in module_or_path
    )
    if is_path:
        module = _load_module_from_path(module_or_path, root=root)
    else:
        try:
            if root:
                with _prepend_sys_path(root):
                    module = importlib.import_module(module_or_path)
            else:
                module = importlib.import_module(module_or_path)
        except Exception as err:
            raise ValueError(f"Unable to import repo map module {module_or_path}: {err}") from err

    try:
        repo_map_class = getattr(module, class_name)
    except AttributeError as err:
        raise ValueError(
            f"Repo map class {class_name!r} was not found in {module_or_path!r}."
        ) from err

    if not isinstance(repo_map_class, type) or not issubclass(repo_map_class, RepoMap):
        raise ValueError(
            f"Repo map class {class_name!r} must inherit from aider.repomap.RepoMap."
        )

    if repo_map_class is not RepoMap:
        source_file = getattr(module, "__file__", None)
        try:
            source_bytes = Path(source_file).read_bytes() if source_file else None
        except OSError:
            source_bytes = None
        if source_bytes is None:
            source_hash = "unknown"
        else:
            source_hash = hashlib.sha256(source_bytes).hexdigest()[:12]
        repo_map_class.TAGS_CACHE_NAMESPACE = (
            f"{repo_map_class.__module__}.{repo_map_class.__qualname__}:{source_hash}"
        )

    return repo_map_class
