"""
Leak check before sharing the kit. Scans every text file in the kit (results/ excluded) for:
- personal-data patterns (email, phone other than the fictional 555-01xx range, SSN) and keys or internal ids;
- terms the private config blocks (e.g. the lender's name, staff names);
- runs of 6+ words copied from the private text in `corpora` (agent instructions, knowledge files, drafts);
- PII in runs of 6+ words copied from `prompt_files` (real prompts the repo's readers already hold). Copying them is
  allowed; a copied run that holds a first name, a 7+ digit number, or an SSN or phone shape is not.
Without a private config only the first check runs. Exit status 1 if anything is found.

run.py uses copied_pii() on every message before it goes to a model.
"""

import re
import zipfile
from functools import lru_cache
from pathlib import Path

from . import config

RULES = [("email address", r"[\w.+-]+@[\w-]+\.[\w.-]+"),
         ("phone number", r"\(?\b\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b"),
         ("SSN", r"\b\d{3}-\d{2}-\d{4}\b"),
         ("custom-GPT id", r"\bg-[0-9a-f]{32}\b"),
         ("API project id", r"\bproj_[A-Za-z0-9]{8,}\b"),
         ("API key", r"\bsk-[A-Za-z0-9_-]{16,}|\bAKIA[0-9A-Z]{16}\b|bedrock-api-key-[A-Za-z0-9]")]
FICTIONAL_PHONE = re.compile(r"555[ .-]01\d\d")
N = 6
SKIP = {"results", "__pycache__", ".git", ".pytest_cache"}
TEXT = {".py", ".md", ".json", ".txt", ".toml", ".cfg", ".yml", ".yaml", ".gitignore"}


def kit_files():
    for p in sorted(config.KIT.rglob("*")):
        if p.is_file() and (p.suffix in TEXT or p.name in TEXT) and not SKIP & set(p.relative_to(config.KIT).parts):
            yield p


def words(text):
    return re.findall(r"[a-z0-9']+", text.lower())


def _read(p):
    """Text of a private file: .xlsx cells, .docx paragraphs, .md/.txt; a folder means every .md/.txt in it."""
    if p.is_dir():
        for f in sorted(p.rglob("*")):
            if f.suffix in (".md", ".txt"):
                yield f.read_text(errors="ignore")
    elif p.suffix == ".xlsx":
        import openpyxl
        for ws in openpyxl.load_workbook(p, read_only=True).worksheets:
            for row in ws.iter_rows(values_only=True):
                yield from (str(c) for c in row if isinstance(c, str))
    elif p.suffix == ".docx":
        yield re.sub(r"<[^>]+>", " ", zipfile.ZipFile(p).read("word/document.xml").decode())
    else:
        yield p.read_text(errors="ignore")


def _grams(paths):
    grams = set()
    for p in paths:
        for text in _read(p):
            t = words(text)
            grams.update(" ".join(t[i:i + N]) for i in range(len(t) - N + 1))
    return grams


@lru_cache(maxsize=None)
def private_grams():
    """6-grams of the private text. Not counted: text that is also in the prompt files (the readers hold it; the PII
    rule covers it) and runs of prompt ids only (e.g. 'nv 146 nv 235 nv 551')."""
    return {g for g in _grams(config.load()["corpora"]) - prompt_grams()
            if not all(re.fullmatch(r"nv|ce|\d+", w) for w in g.split())}


@lru_cache(maxsize=None)
def prompt_grams():
    return _grams(config.load()["prompt_files"])


@lru_cache(maxsize=None)
def first_names():
    """Lowercase first names that are not also ordinary words (the system word lists); None if the lists are missing."""
    names, common = Path("/usr/share/dict/propernames"), Path("/usr/share/dict/words")
    if not (names.exists() and common.exists()):
        return None
    return {n.lower() for n in names.read_text().split()} - {w for w in common.read_text().split() if w.islower()}


def copied_runs(t, grams):
    """The runs of words in t that are covered by 6-grams from grams."""
    covered = [False] * len(t)
    for i in range(len(t) - N + 1):
        if " ".join(t[i:i + N]) in grams:
            covered[i:i + N] = [True] * N
    runs, cur = [], []
    for w, c in zip(t + [""], covered + [False]):
        if c:
            cur.append(w)
        elif cur:
            runs, cur = runs + [cur], []
    return runs


def pii(run):
    """Why a run of words copied from a real prompt may hold PII; empty if nothing is found."""
    names, text = first_names(), " ".join(run)
    why = [f"first name {w!r}" for w in run if names and w in names]
    why += [f"number {w!r}" for w in run if w.isdigit() and len(w) >= 7]
    why += [f"SSN or phone shape {m!r}" for m in re.findall(r"\b\d{3} (?:\d{2}|\d{3}) \d{4}\b", text)]
    return why + ([] if names is not None else ["no system name list, so names cannot be checked"])


def copied_pii(text):
    """Findings for runs of text copied from the prompt files that may hold PII."""
    return [f"{' '.join(r)!r}: {', '.join(why)}" for r in copied_runs(words(text), prompt_grams()) if (why := pii(r))]


def scan():
    cfg = config.load()
    rules = [(name, re.compile(pat)) for name, pat in RULES]
    rules += [(f"blocked term {t!r}", re.compile(rf"\b{re.escape(t)}\b", re.I)) for t in cfg["blocked_terms"]]
    grams, hits, n_copied = private_grams(), [], 0
    for f in kit_files():
        rel = f.relative_to(config.KIT)
        for i, line in enumerate(f.read_text(errors="ignore").splitlines(), 1):
            for name, pat in rules:
                for m in pat.finditer(line):
                    if not (name == "phone number" and FICTIONAL_PHONE.search(m.group())):
                        hits.append(f"{rel}:{i}: {name}: {m.group()!r}")
        t = words(f.read_text(errors="ignore"))
        copied = sorted({" ".join(t[i:i + N]) for i in range(len(t) - N + 1)} & grams)
        hits += [f"{rel}: {N} words copied from private text: {g!r}" for g in copied]
        n_copied += len(copied_runs(t, prompt_grams()))
        hits += [f"{rel}: copied from a real prompt, possible PII: {h}" for h in copied_pii(f.read_text(errors="ignore"))]
    return hits, bool(grams or prompt_grams()), n_copied


def main():
    hits, with_private, n_copied = scan()
    print("\n".join(hits) or "No findings.")
    if n_copied:
        print(f"({n_copied} passages are copied from the prompt files. Allowed: the repo's readers hold those files.)")
    if not with_private:
        print("(No private config: patterns only. Set PROBEKIT_PRIVATE to also check for copied private text.)")
    return 1 if hits else 0
