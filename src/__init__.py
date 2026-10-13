# Prompt Validation Engine for Housing and Lending Compliance
import os
from pathlib import Path

try:
    from dotenv import load_dotenv, find_dotenv
    # Search working directory hierarchy as well as explicit paths
    found = find_dotenv(usecwd=True)
    if found:
        load_dotenv(found)
    load_dotenv(Path(__file__).parent.parent / ".env")
    load_dotenv(Path(__file__).parent.parent.parent / ".env")
except ImportError:
    pass
