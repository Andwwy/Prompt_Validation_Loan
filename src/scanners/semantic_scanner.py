"""
Semantic & LLM Evaluator powered by Google Gemini.
Evaluates complex, implicit, proxy-based, and disparate impact housing/lending discrimination.
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

try:
    from dotenv import load_dotenv
    # Load .env from project root
    load_dotenv(Path(__file__).parent.parent.parent / ".env")
except ImportError:
    pass

from src.models import (
    ViolationItem,
    ViolationCategory,
    ProtectedVariable,
    Severity,
    ValidationResult
)
from src.taxonomy.statutes import STATUTORY_FRAMEWORK
from src.taxonomy.violations import VIOLATION_DEFINITIONS

logger = logging.getLogger(__name__)

SEMANTIC_SYSTEM_PROMPT = """You are a senior regulatory compliance attorney and fair housing evaluator specializing in U.S. housing and credit discrimination law.
Your task is to audit and validate user prompts, marketing copy, tenant screening rules, and mortgage/lending instructions against all federal and state fair housing and fair lending laws as documented in legal treatises and the United States housing discrimination legal framework.

LAWS AND PRECEDENTS TO ENFORCE:
1. Fair Housing Act (Title VIII of Civil Rights Act of 1968, 42 U.S.C. §§ 3601-3619):
   - Prohibits discrimination based on Race, Color, National Origin, Religion, Sex (including Sexual Orientation and Gender Identity per Bostock & HUD 2021).
   - § 3604(c): Prohibits discriminatory statements, advertisements, notices showing preference or limitation.
   - § 3604(a): Prohibits refusal to rent/sell, and demographic/racial steering.
   - § 3605: Prohibits discrimination in real estate financing, loans, appraisals.
2. Fair Housing Amendments Act of 1988 (FHAA, 42 U.S.C. § 3604(f)):
   - Disability (handicap): Mandatory reasonable accommodations (e.g. assistance/service animals exempt from pet policies) and reasonable modifications (e.g. wheelchair ramps).
   - Familial Status: Protection for families with children under 18, pregnancy, adoption. Banning kids or stating "adults only" is illegal (unless qualified 55+ senior housing).
3. Equal Credit Opportunity Act of 1974 (ECOA, 15 U.S.C. § 1691 / Reg B):
   - Prohibits credit/mortgage discrimination based on race, color, religion, national origin, sex, marital status, age, or receipt of public assistance (Section 8 vouchers, SSDI, alimony, child support).
4. Community Reinvestment Act of 1977 (CRA) & Home Mortgage Disclosure Act (HMDA):
   - Prohibits Redlining (denying or limiting credit based on geographic/neighborhood racial composition) and reverse redlining (predatory subprime targeting).
5. Landmark Precedents:
   - Buchanan v. Warley (1917): Racial zoning unconstitutional.
   - Shelley v. Kraemer (1948): Restrictive covenants unenforceable.
   - Texas Dept. of Housing v. Inclusive Communities Project (2015): Disparate Impact (facially neutral policies that disproportionately harm protected classes without legitimate business necessity).
6. HUD Regulatory Guidance:
   - HUD 2016 Criminal Records: Blanket bans on arrest records or criminal history produce unlawful disparate impact.
   - HUD 2016 Limited English Proficiency: English-only requirements operate as national origin discrimination proxies.
   - HUD Digital Ad Targeting Precedents: Prohibits excluding protected classes or zip codes from housing/lending advertisements.

EVALUATION INSTRUCTIONS:
- Analyze the prompt thoroughly. Look for both overt discrimination AND subtle proxies (e.g., coded demographic steering, maternity leave loan delays, refusing assistance animals under pet bans, excluding low-income zip codes).
- If the prompt is completely legal and compliant (e.g. standard credit score checks, standard security deposit, physical property descriptions), return "is_compliant": true, "risk_score": 0.0, and empty violations list.
- If violations exist, cite the exact law, statutory reference, protected variable, severity, and provide a clear explanation and compliant rewrite.

OUTPUT FORMAT:
Return ONLY a valid JSON object matching this schema:
{
  "is_compliant": false,
  "risk_score": 0.85,
  "overall_severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
  "summary": "Brief summary of compliance finding",
  "violations": [
    {
      "category": "One of the legal violation categories",
      "law_cited": "e.g., Fair Housing Act (42 U.S.C. § 3604(c))",
      "statutory_reference": "e.g., 42 U.S.C. § 3604(c)",
      "protected_variable": "race | color | national_origin | religion | sex | sexual_orientation | gender_identity | familial_status | disability | marital_status | age | source_of_income | criminal_history | geographic_redlining | language_proficiency",
      "flagged_text": "Exact phrase from prompt",
      "severity": "CRITICAL | HIGH | MEDIUM | LOW",
      "explanation": "Legal rationale",
      "remediation_guidance": "How to make it compliant"
    }
  ],
  "suggested_compliant_prompt": "An affirmative, legally compliant rewrite of the user's prompt"
}
"""


class SemanticScanner:
    """Invokes Gemini LLM for deep grounded legal compliance checks."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def scan(self, prompt: str, context: str = "general") -> Optional[Dict[str, Any]]:
        """
        Analyze prompt with Gemini.
        Returns parsed JSON dict or None if API key not available or request fails.
        """
        if not self.is_configured():
            logger.info("Gemini API key not configured. Skipping semantic LLM scan.")
            return None

        # Try google.genai first (official modern SDK)
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            user_message = f"Context: {context}\nPrompt to validate:\n\"\"\"{prompt}\"\"\""

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=SEMANTIC_SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )

            text_output = response.text
            return json.loads(text_output)
        except Exception as e_genai:
            logger.warning(f"google.genai call failed: {e_genai}. Trying fallback google.generativeai...")

        # Fallback to google.generativeai
        try:
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=self.api_key)
            model = legacy_genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=SEMANTIC_SYSTEM_PROMPT,
                generation_config={"response_mime_type": "application/json", "temperature": 0.1}
            )
            response = model.generate_content(f"Context: {context}\nPrompt to validate:\n\"\"\"{prompt}\"\"\"")
            return json.loads(response.text)
        except Exception as e_legacy:
            logger.error(f"Both Gemini SDKs failed: {e_legacy}")
            return None
