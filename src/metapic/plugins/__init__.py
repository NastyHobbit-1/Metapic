from importlib import import_module
from pkgutil import iter_modules
from pathlib import Path
from typing import Any, Dict, List

__all__ = ["load_plugins", "run_parse_chain"]

PKG_NAME = __name__

def load_plugins() -> List[Any]:
    plugins: List[Any] = []
    pkg_path = Path(__file__).parent
    for _, name, ispkg in iter_modules([str(pkg_path)]):
        if ispkg:
            continue
        mod_name = f"{PKG_NAME}.{name}"
        try:
            plugins.append(import_module(mod_name))
        except Exception as e:
            print(f"[WARN] Failed to load plugin {mod_name}: {e}")
    return plugins

def run_parse_chain(raw: Dict[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for plugin in load_plugins():
        try:
            parsed = getattr(plugin, "parse", None)
            if parsed is None:
                continue
            data = parsed(raw)
            if data:
                result.update(data)
        except Exception as e:
            print(f"[WARN] plugin {plugin.__name__} failed: {e}")
    return result
