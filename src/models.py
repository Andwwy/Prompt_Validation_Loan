"""
Data models and schemas for Housing & Lending Prompt Validation.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ProtectedVariable(str, Enum):
    RACE = "race"
    COLOR = "color"
    NATIONAL_ORIGIN = "national_origin"
    RELIGION = "religion"
    SEX = "sex"
    SEXUAL_ORIENTATION = "sexual_orientation"
    GENDER_IDENTITY = "gender_identity"
    FAMILIAL_STATUS = "familial_status"
    DISABILITY = "disability"
    MARITAL_STATUS = "marital_status"
    AGE = "age"
    SOURCE_OF_INCOME = "source_of_income"
    CRIMINAL_HISTORY = "criminal_history"
    GEOGRAPHIC_LOCATION = "geographic_redlining"
    LANGUAGE_PROFICIENCY = "language_proficiency"


class ViolationCategory(str, Enum):
    DISCRIMINATORY_ADVERTISING = "Discriminatory Advertising & Statements"
    STEERING = "Racial & Demographic Steering"
    REDLINING = "Geographic Redlining & Credit Denial"
    REVERSE_REDLINING_PREDATORY = "Reverse Redlining & Predatory Targeting"
    CREDIT_MORTGAGE_DISPARATE_TREATMENT = "Credit & Mortgage Disparate Treatment"
    DISPARATE_IMPACT = "Facially Neutral Disparate Impact"
    REASONABLE_ACCOMMODATION_FAILURE = "Denial of Reasonable Accommodation"
    REASONABLE_MODIFICATION_FAILURE = "Denial of Reasonable Modification"
    RESTRICTIVE_COVENANTS_OR_ZONING = "Restrictive Covenants & Exclusionary Filtering"
    HARASSMENT_QUID_PRO_QUO = "Harassment & Quid Pro Quo Coercion"
    SOURCE_OF_INCOME_EXCLUSION = "Source of Income & Voucher Exclusion"
    CRIMINAL_HISTORY_BLANKET_EXCLUSION = "Blanket Criminal Record Exclusion"
    LANGUAGE_LEP_EXCLUSION = "Limited English Proficiency (LEP) Exclusion"


class ViolationItem(BaseModel):
    category: ViolationCategory
    law_cited: str = Field(..., description="Name of the governing law or precedent")
    statutory_reference: str = Field(..., description="Statute section or legal citation (e.g., 42 U.S.C. § 3604(c))")
    protected_variable: ProtectedVariable
    flagged_text: Optional[str] = Field(None, description="Exact phrase or substring from the prompt triggering the violation")
    severity: Severity = Field(default=Severity.HIGH)
    explanation: str = Field(..., description="Legal rationale for why this constitutes housing/lending discrimination")
    remediation_guidance: str = Field(..., description="Guidance on how to rephrase or adjust policy compliantly")


class ValidationResult(BaseModel):
    prompt: str
    is_compliant: bool
    risk_score: float = Field(..., ge=0.0, le=1.0, description="0.0 (Clean/Compliant) to 1.0 (Critical Multi-Violation)")
    overall_severity: Optional[Severity] = None
    summary: str
    violations: List[ViolationItem] = Field(default_factory=list)
    suggested_compliant_prompt: Optional[str] = None
    audit_metadata: Dict[str, Any] = Field(default_factory=dict)


class ValidationRequest(BaseModel):
    prompt: str
    context: str = Field(default="general", description="Context: 'rental_listing', 'mortgage_underwriting', 'ad_targeting', 'general'")
    enable_semantic_analysis: bool = True
    api_key: Optional[str] = None
