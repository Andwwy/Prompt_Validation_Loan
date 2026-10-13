"""
FastAPI Server & REST API for Housing & Lending Prompt Validation.
"""

import os
from pathlib import Path
from typing import Dict, Any, List

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from src.models import ValidationRequest, ValidationResult
from src.engine import PromptValidator
from src.taxonomy.statutes import STATUTORY_FRAMEWORK
from src.taxonomy.violations import VIOLATION_DEFINITIONS
from src.taxonomy.protected_vars import PROTECTED_VARIABLES_CONFIG

app = FastAPI(
    title="Fair Housing & Lending Prompt Validator",
    description="Validation engine auditing prompts against FHA, ECOA, CRA, HMDA, and HUD regulations.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

validator = PromptValidator()

STATIC_DIR = Path(__file__).parent / "static"


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "gemini_configured": validator.semantic_scanner.is_configured(),
        "version": "1.0.0"
    }


@app.post("/api/validate", response_model=ValidationResult)
def validate_prompt(req: ValidationRequest):
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt text cannot be empty.")

    result = validator.validate(
        prompt=req.prompt,
        context=req.context,
        enable_semantic=req.enable_semantic_analysis,
        api_key_override=req.api_key
    )
    return result


@app.get("/api/benchmarks")
def get_benchmarks():
    benchmark_file = Path(__file__).parent.parent / "tests" / "benchmark_cases.json"
    if benchmark_file.exists():
        import json
        with open(benchmark_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


@app.get("/api/statutes")
def get_statutes():
    return {
        "statutes": STATUTORY_FRAMEWORK,
        "violations": {k.value: v for k, v in VIOLATION_DEFINITIONS.items()},
        "protected_variables": {k.value: v for k, v in PROTECTED_VARIABLES_CONFIG.items()}
    }


@app.post("/api/configure-key")
def configure_key(payload: Dict[str, str]):
    api_key = payload.get("api_key", "").strip()
    if not api_key:
        raise HTTPException(status_code=400, detail="API key is required.")
    validator.set_api_key(api_key)
    os.environ["GEMINI_API_KEY"] = api_key
    return {"status": "success", "gemini_configured": validator.semantic_scanner.is_configured()}


# Mount static assets
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Web UI static files not found."}
