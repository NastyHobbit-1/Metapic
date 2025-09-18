from __future__ import annotations
import re
from typing import Dict, Any

KNOWN_SAMPLERS = {
    "Euler a", "Euler", "DPM++ 2M", "DPM++ SDE Karras", "DDIM", "UniPC", "Heun",
}

class Normalizer:
    def __init__(self) -> None:
        pass

    def parse_text_block(self, text: str) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        if not text:
            return out

        # heuristic sampler
        tl = text.lower()
        for s in KNOWN_SAMPLERS:
            if s.lower() in tl:
                out["sampler"] = s
                break

        # steps
        m = re.search(r"steps?\s*[:=\-]?\s*(\d+)", text, re.I)
        if m:
            out["steps"] = int(m.group(1))

        # cfg
        m = re.search(r"cfg\s*(scale)?\s*[:=\-]?\s*([\d.]+)", text, re.I)
        if m:
            out["cfg"] = float(m.group(2))

        # seed
        m = re.search(r"seed\s*[:=\-]?\s*(\d+)", text, re.I)
        if m:
            out["seed"] = int(m.group(1))

        return out
