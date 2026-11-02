"""
Settings. The kit needs none: results, the spend ledger and the lock file default to probekit/results/.

A private folder (env PROBEKIT_PRIVATE) holds what must not go in the repo: real agent exports, scenario overlays,
knowledge excerpts, the shared ledger and budget, and the private text the leak check scans. `prompt_files` lists the
real prompt files that everyone who reads the repo already holds: text copied from them may be in the kit, but only
without PII. Its config.json uses the keys below; paths are relative to that folder.
"""

import json
import os
from functools import lru_cache
from pathlib import Path

KIT = Path(__file__).resolve().parent
PATH_KEYS = ("results_dir", "ledger", "spend_lock", "agents_dir", "excerpts_dir")


@lru_cache(maxsize=None)
def load():
    cfg = {"private": None, "results_dir": KIT / "results", "ledger": KIT / "results" / "spend.jsonl",
           "spend_lock": KIT / "results" / "SPEND_LOCK", "budget_usd": 5.0, "default_backend": None,
           "agents_dir": None, "agents": {}, "excerpts_dir": None, "mantle": {}, "corpora": [], "prompt_files": [],
           "blocked_terms": [], "overlays": {}}
    if os.environ.get("PROBEKIT_PRIVATE"):
        priv = Path(os.environ["PROBEKIT_PRIVATE"]).expanduser().resolve()
        raw = json.loads((priv / "config.json").read_text())
        cfg.update({k: v for k, v in raw.items() if not k.startswith("_")})
        cfg.update({k: (priv / raw[k]).resolve() for k in PATH_KEYS if k in raw})
        for key in ("corpora", "prompt_files"):
            cfg[key] = [(priv / c).resolve() for c in raw.get(key, [])]
        cfg["private"] = priv
        if (priv / "overlays.json").exists():
            cfg["overlays"] = json.loads((priv / "overlays.json").read_text())
    if os.environ.get("PROBEKIT_BUDGET_USD"):
        cfg["budget_usd"] = float(os.environ["PROBEKIT_BUDGET_USD"])
    return cfg
