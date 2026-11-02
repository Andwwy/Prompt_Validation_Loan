"""
Scenarios: one JSON file per probe in scenarios/ (fields in scenarios/README.md). Every arm sees the same messages
except the arm's slots. A private overlay (overlays.json) can replace top-level fields of a scenario, e.g. the
real prompt wording, so the shared file holds none of it.
"""

import json
import random

from . import config, docs

DIR = config.KIT / "scenarios"


def ids():
    return sorted(p.stem for p in DIR.glob("*.json") if not p.stem.startswith("_"))


def load(sid):
    sc = json.loads((DIR / f"{sid}.json").read_text())
    sc.update(config.load()["overlays"].get(sid, {}))
    sc["id"] = sid
    return sc


def baseline(sc):
    return sc.get("baseline") or sorted(sc["arms"])[0]


def slots(sc, arm):
    cue = sc["arms"][arm]
    return {**sc.get("slots", {}), **(cue if isinstance(cue, dict) else {"cue": cue})}


def messages(sc, arm, rep):
    """The loan officer's messages for one run, and the menu order (shuffled with the same seed in every arm)."""
    s, order = slots(sc, arm), None
    if "menu" in sc:
        order = list(sc["menu"])
        random.Random(rep).shuffle(order)
        s["menu"] = "\n".join(f"{k}: {sc['menu'][k]}" for k in order)
    if "doc" in sc:
        s["doc"] = docs.build(sc["doc"], s)
    first = [sc["paraphrases"][rep % len(sc["paraphrases"])]] if "paraphrases" in sc else []
    return [t.format(**s) for t in first + sc["turns"]], order


def excerpt(name):
    """A knowledge-file excerpt: the private copy (the agent's own file) if configured, else the kit's own."""
    for d in (config.load()["excerpts_dir"], config.KIT / "excerpts"):
        if d and (d / f"{name}.txt").exists():
            return (d / f"{name}.txt").read_text()
    raise FileNotFoundError(f"knowledge excerpt {name!r} not found")


def system_prompt(sc, agent):
    system = agent.system
    if "excerpt" in sc:
        system += "\n\n# Knowledge file excerpt\n\n" + excerpt(sc["excerpt"])
    if "date" in sc:  # ChatGPT's own system prompt carries the date; without it the agent guesses one
        system += f"\n\nCurrent date: {sc['date']}."
    return system
