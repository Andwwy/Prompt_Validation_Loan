"""
Core PromptValidator Engine.
Orchestrates rule scanning, proxy detection, and Gemini semantic analysis.
"""

import time
from typing import Optional, List, Dict, Any

from src.models import (
    ValidationResult,
    ViolationItem,
    Severity,
    ValidationRequest
)
from src.scanners.rule_scanner import RuleScanner
from src.scanners.proxy_scanner import ProxyScanner
from src.scanners.semantic_scanner import SemanticScanner
from src.rewriter import PromptRewriter
from src.models import ViolationCategory, ProtectedVariable


def normalize_category(cat_str: str) -> ViolationCategory:
    if not cat_str:
        return ViolationCategory.DISCRIMINATORY_ADVERTISING
    cat_lower = str(cat_str).lower()
    for member in ViolationCategory:
        if member.value.lower() in cat_lower or cat_lower in member.value.lower():
            return member
    if "advertis" in cat_lower or "notice" in cat_lower or "statement" in cat_lower:
        return ViolationCategory.DISCRIMINATORY_ADVERTISING
    if "steer" in cat_lower:
        return ViolationCategory.STEERING
    if "redlin" in cat_lower:
        return ViolationCategory.REDLINING
    if "disability" in cat_lower or "accommodat" in cat_lower:
        return ViolationCategory.REASONABLE_ACCOMMODATION_FAILURE
    if "modification" in cat_lower:
        return ViolationCategory.REASONABLE_MODIFICATION_FAILURE
    if "credit" in cat_lower or "mortgage" in cat_lower or "marital" in cat_lower:
        return ViolationCategory.CREDIT_MORTGAGE_DISPARATE_TREATMENT
    if "income" in cat_lower or "voucher" in cat_lower:
        return ViolationCategory.SOURCE_OF_INCOME_EXCLUSION
    if "arrest" in cat_lower or "criminal" in cat_lower:
        return ViolationCategory.CRIMINAL_HISTORY_BLANKET_EXCLUSION
    if "english" in cat_lower or "language" in cat_lower or "lep" in cat_lower:
        return ViolationCategory.LANGUAGE_LEP_EXCLUSION
    return ViolationCategory.DISPARATE_IMPACT


def normalize_variable(var_str: str) -> ProtectedVariable:
    if not var_str:
        return ProtectedVariable.RACE
    var_lower = str(var_str).lower().replace(" ", "_").replace("-", "_")
    for member in ProtectedVariable:
        if member.value in var_lower or var_lower in member.value:
            return member
    if "child" in var_lower or "fam" in var_lower:
        return ProtectedVariable.FAMILIAL_STATUS
    if "disab" in var_lower or "handicap" in var_lower:
        return ProtectedVariable.DISABILITY
    if "relig" in var_lower or "faith" in var_lower:
        return ProtectedVariable.RELIGION
    if "gender" in var_lower or "trans" in var_lower:
        return ProtectedVariable.GENDER_IDENTITY
    if "sex" in var_lower or "orient" in var_lower or "gay" in var_lower or "lesbian" in var_lower:
        return ProtectedVariable.SEXUAL_ORIENTATION
    if "incom" in var_lower or "voucher" in var_lower or "assist" in var_lower:
        return ProtectedVariable.SOURCE_OF_INCOME
    if "crimin" in var_lower or "arrest" in var_lower:
        return ProtectedVariable.CRIMINAL_HISTORY
    if "zip" in var_lower or "geo" in var_lower or "redlin" in var_lower:
        return ProtectedVariable.GEOGRAPHIC_LOCATION
    return ProtectedVariable.RACE


def normalize_severity(sev_str: str) -> Severity:
    if not sev_str:
        return Severity.HIGH
    sev_upper = str(sev_str).upper()
    for member in Severity:
        if member.value == sev_upper:
            return member
    if "CRIT" in sev_upper:
        return Severity.CRITICAL
    if "MED" in sev_upper:
        return Severity.MEDIUM
    if "LOW" in sev_upper:
        return Severity.LOW
    return Severity.HIGH


class PromptValidator:
    """Enterprise Prompt Validation Engine for Housing & Lending Compliance."""

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.rule_scanner = RuleScanner()
        self.proxy_scanner = ProxyScanner()
        self.semantic_scanner = SemanticScanner(api_key=gemini_api_key)
        self.rewriter = PromptRewriter()

    def set_api_key(self, api_key: str):
        """Update the Gemini API key at runtime."""
        self.semantic_scanner = SemanticScanner(api_key=api_key)

    def validate(
        self,
        prompt: str,
        context: str = "general",
        enable_semantic: bool = True,
        api_key_override: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate a prompt against all federal and state housing & credit discrimination laws.
        """
        start_time = time.perf_counter()
        violations: List[ViolationItem] = []
        checks_performed = ["rule_scanner", "proxy_scanner"]

        # Step 1: Deterministic fast-path rule check
        rule_violations = self.rule_scanner.scan(prompt)
        violations.extend(rule_violations)

        # Step 2: Subtle proxy and disparate impact check
        proxy_violations = self.proxy_scanner.scan(prompt)
        violations.extend(proxy_violations)

        # Step 3: Semantic LLM scan (Gemini)
        semantic_report: Optional[Dict[str, Any]] = None
        scanner_to_use = self.semantic_scanner
        if api_key_override:
            scanner_to_use = SemanticScanner(api_key=api_key_override)

        if enable_semantic and scanner_to_use.is_configured():
            checks_performed.append("gemini_semantic_evaluator")
            semantic_report = scanner_to_use.scan(prompt, context=context)

            if semantic_report and isinstance(semantic_report, dict):
                # Parse semantic violations from LLM output
                sem_violations = semantic_report.get("violations", [])
                for sv in sem_violations:
                    try:
                        norm_cat = normalize_category(sv.get("category", ""))
                        norm_var = normalize_variable(sv.get("protected_variable", ""))
                        norm_sev = normalize_severity(sv.get("severity", "HIGH"))
                        flagged = sv.get("flagged_text", "").strip()

                        # Deduplicate if exact category and span already captured
                        already_flagged = any(
                            (v.flagged_text and flagged and flagged.lower() in v.flagged_text.lower())
                            and (v.category == norm_cat)
                            for v in violations
                        )
                        if not already_flagged:
                            violations.append(
                                ViolationItem(
                                    category=norm_cat,
                                    law_cited=sv.get("law_cited", "Fair Housing Act"),
                                    statutory_reference=sv.get("statutory_reference", "42 U.S.C. § 3604"),
                                    protected_variable=norm_var,
                                    flagged_text=flagged or None,
                                    severity=norm_sev,
                                    explanation=sv.get("explanation", "Potential discriminatory implication under fair housing statutes."),
                                    remediation_guidance=sv.get("remediation_guidance", "Modify prompt criteria to be neutral.")
                                )
                            )
                    except Exception as e:
                        pass

        # Step 4: Calculate Risk Score and Overall Severity
        is_compliant = len(violations) == 0
        overall_severity: Optional[Severity] = None
        risk_score = 0.0

        if not is_compliant:
            severities = [v.severity for v in violations]
            if Severity.CRITICAL in severities:
                overall_severity = Severity.CRITICAL
                risk_score = min(1.0, 0.75 + (0.05 * len(violations)))
            elif Severity.HIGH in severities:
                overall_severity = Severity.HIGH
                risk_score = min(0.9, 0.55 + (0.05 * len(violations)))
            elif Severity.MEDIUM in severities:
                overall_severity = Severity.MEDIUM
                risk_score = min(0.7, 0.35 + (0.05 * len(violations)))
            else:
                overall_severity = Severity.LOW
                risk_score = 0.25

            # If semantic scanner gave a risk score, average it
            if semantic_report and "risk_score" in semantic_report:
                try:
                    sem_score = float(semantic_report["risk_score"])
                    risk_score = round(max(risk_score, sem_score), 2)
                except (ValueError, TypeError):
                    pass
        else:
            risk_score = 0.0

        # Step 5: Synthesize Summary
        if is_compliant:
            summary = "Prompt is legally compliant. No housing or credit discrimination violations detected."
            suggested_prompt = prompt
        else:
            cat_names = list(dict.fromkeys(v.category.value if hasattr(v.category, 'value') else str(v.category) for v in violations))
            summary = f"Flagged {len(violations)} violation(s) under fair housing and lending laws: {', '.join(cat_names)}."

            # Determine compliant rewrite
            if semantic_report and semantic_report.get("suggested_compliant_prompt"):
                suggested_prompt = semantic_report["suggested_compliant_prompt"]
            else:
                suggested_prompt = self.rewriter.rewrite_prompt(prompt, violations)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return ValidationResult(
            prompt=prompt,
            is_compliant=is_compliant,
            risk_score=risk_score,
            overall_severity=overall_severity,
            summary=summary,
            violations=violations,
            suggested_compliant_prompt=suggested_prompt,
            audit_metadata={
                "checks_performed": checks_performed,
                "execution_time_ms": duration_ms,
                "semantic_evaluator_active": "gemini_semantic_evaluator" in checks_performed,
                "violations_count": len(violations)
            }
        )
