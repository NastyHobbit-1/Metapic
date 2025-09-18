from __future__ import annotations
import re
from pathlib import Path
from typing import Iterable, Dict
from .models import ImageMeta

SAFE = re.compile(r"[^A-Za-z0-9._-]+")

def safe_name(text: str) -> str:
    return SAFE.sub("-", text).strip("-_")

class _SafeDict(dict):
    # any unknown {field} becomes ""
    def __missing__(self, key):
        return ""

def title_hint(self) -> str:
    parts = []
    base = self.model or self.base_model or self.method
    if base:
        parts.append(str(base))
    if self.steps is not None:
        parts.append(f"s{self.steps}")
    if self.cfg is not None:
        cfg_str = f"{self.cfg}".rstrip("0").rstrip(".")
        parts.append(f"cfg{cfg_str}")
    if self.seed is not None:
        parts.append(f"seed{self.seed}")
    if not parts:
        try:
            parts.append(Path(self.path).stem)
        except Exception:
            parts.append("image")
    return "-".join(parts)

def plan_rename(items: Iterable[ImageMeta], pattern: str = "{title}-{i:04d}") -> Dict[str, str]:
    plan: Dict[str, str] = {}
    for i, m in enumerate(items, start=1):
        # Expose all ImageMeta fields + index + computed title
        ctx = m.model_dump()
        ctx["i"] = i
        ctx["title"] = m.title_hint()

        # tolerant formatting: missing keys -> ""
        stem = safe_name(pattern.format_map(_SafeDict(ctx)))
        if not stem:
            # last resort: basename + index
            stem = f"{Path(m.path).stem}-{i:04d}"

        src = Path(m.path)
        dst = src.with_name(f"{stem}{src.suffix}")
        plan[str(src)] = str(dst)
    return plan
