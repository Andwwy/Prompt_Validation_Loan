"""
Prompt Rewriter and Remediation Engine.
Generates affirmative, compliant alternative prompts that achieve
legitimate business objectives without discriminatory criteria.
"""

import re
from typing import List, Optional
from src.models import ViolationItem, ProtectedVariable


class PromptRewriter:
    """Remediates non-compliant prompts into legally permissible alternatives."""

    CLEANUP_REPLACEMENTS = [
        # Familial status
        (r"\b(strictly\s+)?no\s+(children|kids|babies|toddlers|strollers)(\s+(or|and)\s+(children|kids|babies|toddlers))?\b", ""),
        (r"\b(adults\s+only|child[- ]free|strictly\s+adults)\b", ""),
        (r"\b(mature\s+(adults|singles|couples)\s+only|not\s+suitable\s+for\s+(children|kids|families))\b", ""),
        (r"\bperfect\s+for\s+(a\s+)?(single\s+(quiet\s+)?professional|bachelor)\b", "spacious living space suitable for any qualified applicant"),
        (r"\bcouples\s+without\s+children\b", "qualified applicants"),

        # Religion
        (r"\b(christian|jewish|catholic|protestant|muslim|islamic|mormon|hindu)\s+(only|preferred|community|values|tenants|homeowners)\b", "all community members"),
        (r"\b(church[- ]go(ers|ing)|god[- ]fearing)\s+(only|preferred)\b", "all qualified residents"),
        (r"\bnear\s+(the\s+)?(church|mosque|synagogue)\s+for\s+(believers|fellow\s+christians)\b", "conveniently located near neighborhood places of worship"),

        # Race & National Origin
        (r"\b(white|caucasian|black|african\s+american|asian|hispanic|latino)\s+(only|preferred|tenants|residents)\b", "equal housing opportunity applicants"),
        (r"\bno\s+(blacks|african\s+americans|whites|asians|hispanics|minorities)\b", ""),
        (r"\b(english\s+only|must\s+speak\s+(fluent\s+)?english|fluent\s+english\s+speakers?\s+only|no\s+spanish\s+speakers)\b", ""),
        (r"\b(citizens\s+only|us\s+born\s+citizens?\s+only|american\s+born\s+only)\b", "all applicants with lawful residence"),

        # Disability & Animals
        (r"\bno\s+(service|assistance|therapy|guide|support)\s+animals?\b", "assistance and service animals permitted per federal law"),
        (r"\bno\s+emotional\s+support\s+animals?\b", "assistance animals accommodated per fair housing guidelines"),
        (r"\bpet\s+fee\s+for\s+(service|assistance|support)\s+animals?\b", "no fee for assistance animals"),
        (r"\b(no\s+(wheelchairs|wheelchair\s+ramps|grab\s+bars)|able[- ]bodied\s+only)\b", "accessible accommodations available"),

        # Source of Income & Vouchers
        (r"\b(no\s+section\s+8|no\s+vouchers|section\s+8\s+not\s+accepted|no\s+housing\s+choice\s+vouchers?)\b", "all lawful sources of income accepted, including Section 8 vouchers"),
        (r"\b(no\s+government\s+(subsidies|assistance|vouchers)|no\s+welfare)\b", "verifiable income from all lawful sources accepted"),
        (r"\bw2\s+income\s+only\b", "verifiable proof of income accepted"),

        # Criminal Records
        (r"\b(no\s+arrest\s+records?|clean\s+arrest\s+record\s+required|any\s+arrest\s+disqualifies)\b", "individualized background check considering relevant convictions only"),
        (r"\bblanket\s+ban\s+on\s+all\s+(criminal|felony)\s+records?\b", "case-by-case review of criminal convictions related to resident safety"),

        # Credit / Marital Status
        (r"\b(married\s+couples?\s+only|unmarried\s+applicants?\s+not\s+eligible)\b", "all qualified applicants"),
        (r"\b(husband\s+must\s+co-?sign|spouse\s+must\s+co-?sign\s+regardless)\b", "individual credit qualification assessed based on applicant's sole credit profile"),

        # Redlining / Steering
        (r"\b(redline\s+(this|the|those)\s+(zip\s+codes?|neighborhoods?)|exclude\s+(minority|low[- ]income|inner[- ]city)\s+zip\s+codes?)\b", "market loans equally across all service areas based on neutral credit underwriting standards")
    ]

    def rewrite_prompt(self, prompt: str, violations: List[ViolationItem]) -> str:
        """Create a compliant rewrite of the prompt."""
        if not violations:
            return prompt

        remediated = prompt
        for pattern, replacement in self.CLEANUP_REPLACEMENTS:
            remediated = re.sub(pattern, replacement, remediated, flags=re.IGNORECASE)

        # Clean leftover orphaned conjunctions/modifiers
        remediated = re.sub(r"\b(strictly|strictly\s+no)\s*(or|and)?\b", "", remediated, flags=re.IGNORECASE)
        remediated = re.sub(r"[,;]\s*[,;]", ",", remediated)
        remediated = re.sub(r"\s+([,.\?!])", r"\1", remediated)
        remediated = re.sub(r"[,;]\s*\.", ".", remediated)
        remediated = re.sub(r"\.\s*\.", ".", remediated)
        remediated = re.sub(r"\s{2,}", " ", remediated).strip()

        # Append standard compliance affirmation if substantial edits occurred
        has_housing_content = any(kw in remediated.lower() for kw in ["rent", "apartment", "home", "unit", "lease", "tenant", "listing"])
        if has_housing_content and "equal housing" not in remediated.lower():
            remediated += " (Compliant with Equal Housing Opportunity standards)."

        return remediated
