"""
Real loan-officer prompts from the private prompt files, by id: "NV 559" is spreadsheet row 559 of the file the private
config registers as NV. A scenario names the id; the text is read here at run time, so it never goes in a scenario
file and stays off the repo.

The text of a row is its prompt column: the rightmost header that names text, question or prompt (e.g. "Question",
"Full user text"), else the last column. .xlsx needs openpyxl; .csv needs nothing.
"""

import csv
import re
from functools import lru_cache

from . import config

HEADER = re.compile(r"text|question|prompt", re.I)


def _rows(path):
    if path.suffix == ".csv":
        with path.open(newline="", encoding="utf-8-sig") as f:
            yield from csv.reader(f)
        return
    import openpyxl
    ws = openpyxl.load_workbook(path, read_only=True).worksheets[0]
    yield from ws.iter_rows(values_only=True)


@lru_cache(maxsize=None)
def table(prefix):
    """{row number: prompt text} for the file registered as prefix. Row 1 is the header."""
    files = config.load()["prompt_files"]
    if prefix not in files:
        raise KeyError(f"no prompt file registered as {prefix!r}: add it to prompt_files in the private config "
                       f"(registered: {', '.join(files) or 'none'})")
    rows = iter(_rows(files[prefix]))
    header = [str(h or "") for h in next(rows)]
    col = max((i for i, h in enumerate(header) if HEADER.search(h)), default=len(header) - 1)
    return {n: str(row[col]).strip() for n, row in enumerate(rows, 2)
            if col < len(row) and row[col] is not None and str(row[col]).strip()}


def parse(pid):
    m = re.fullmatch(r"\s*([A-Za-z]+)\s*-?\s*(\d+)\s*", pid)
    if not m:
        raise ValueError(f"prompt id {pid!r}: expected a prefix and a row number, e.g. 'NV 559'")
    return m.group(1).upper(), int(m.group(2))


def text(pid):
    prefix, n = parse(pid)
    rows = table(prefix)
    if n not in rows:
        raise KeyError(f"prompt {pid!r}: row {n} of the {prefix} file is empty or missing")
    return rows[n]


def search(words, prefixes=None):
    """(id, text) for every prompt that holds all the words (case-insensitive)."""
    words = [w.lower() for w in words]
    for prefix in prefixes or config.load()["prompt_files"]:
        for n, t in table(prefix).items():
            if all(w in t.lower() for w in words):
                yield f"{prefix} {n}", t
