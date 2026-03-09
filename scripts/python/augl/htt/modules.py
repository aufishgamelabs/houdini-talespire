"""
Provides methods for managing houdini modules.
"""

import sys
from importlib import reload
from pathlib import Path


def reload_modules() -> None:
    """
    Reloads all modules in the htt package.
    """

    package = "augl.htt"
    if package not in sys.modules:
        return

    pkg = sys.modules[package]
    path = Path(str(pkg.__path__[0]))

    modules = []
    for py_file in path.rglob("*.py"):
        rel_path = py_file.relative_to(path)
        if py_file.name == "__init__.py":
            modules.append(
                f"{package}." + ".".join(rel_path.with_suffix("").parts[:-1])
            )
        else:
            modules.append(
                f"{package}." + ".".join(rel_path.with_suffix("").parts)
            )

    for module in modules:
        if module in sys.modules:
            try:
                reload(sys.modules[module])
                print(f"Reloaded module: {module}")
            except ImportError as e:
                print(f"{module} failed to reload: {e}")
