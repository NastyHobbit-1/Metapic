from __future__ import annotations
import json
import os
import re
from typing import Dict, Any

# Keys in exiftool output that may contain A1111 "parameters" blocks
SIDE_KEYS = [
    "parameters",  # A1111 style block
    "Software",    # sometimes includes SD hints
]

def _from_parameters_block(text: str) -> Dict[str, Any]:
    if not text:
        return {}
    out: Dict[str, Any] = {}

    # prompt / negative prompt split
    if "Negative prompt:" in text:
        p, n = text.split("Negative prompt:", 1)
        out["prompt"] = p.strip().strip("\n, ")
        out["negative_prompt"] = n.split("\n")[0].strip().strip(", ")
    else:
        out["prompt"] = text.strip()

    # sampler, steps, cfg, seed
    for key, pat, cast in [
        ("sampler", r"Sampler:\s*([^,\n]+)", str),
        ("steps", r"Steps?:\s*(\d+)", int),
        ("cfg", r"CFG(?:\s*Scale)?:\s*([\d.]+)", float),
        ("seed", r"Seed:\s*(\d+)", int),
    ]:
        m = re.search(pat, text, re.I)
        if m:
            out[key] = cast(m.group(1))
    return out

def parse(raw: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}

    # Sidecar JSON (e.g., ComfyUI) with same stem as image
    sourcefile = raw.get("SourceFile") or raw.get("SourceFileName")
    if sourcefile:
        jpath = os.path.splitext(sourcefile)[0] + ".json"
        try:
            if os.path.exists(jpath):
                with open(jpath, "rb") as f:
                    side = json.loads(f.read().decode("utf-8", errors="ignore"))
                if isinstance(side, dict):
                    out.update({
                        "model": side.get("model"),
                        "base_model": side.get("base_model") or side.get("base"),
                        "sampler": side.get("sampler"),
                        "scheduler": side.get("scheduler"),
                        "steps": side.get("steps"),
                        "cfg": side.get("cfg") or side.get("cfg_scale"),
                        "seed": side.get("seed"),
                        "prompt": side.get("prompt"),
                        "negative_prompt": side.get("negative_prompt"),
                        "method": side.get("method") or side.get("pipeline"),
                    })
        except Exception:
            # Ignore sidecar parse failures silently
            pass

    # A1111-style parameters embedded in EXIF
    for k in SIDE_KEYS:
        text = raw.get(k)
        if isinstance(text, str) and text.strip():
            out.update(_from_parameters_block(text))

    # General EXIF fallbacks
    mapping = [
        ("ImageWidth", "width"),
        ("ImageHeight", "height"),
        ("MIMEType", "format"),
        ("FileSize#", "size_bytes"),  # numeric bytes if present
    ]
    for src, dst in mapping:
        if raw.get(src) is not None:
            out[dst] = raw.get(src)

    return {k: v for k, v in out.items() if v not in (None, "")}
