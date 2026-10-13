"""
Proxy and Disparate Impact Scanner.
Identifies subtle demographic proxies, algorithmic targeting exclusions,
and facially neutral restrictions that produce unlawful discriminatory effects.
"""

import re
from typing import List
from src.models import ViolationItem, ViolationCategory, ProtectedVariable, Severity


class ProxyScanner:
    """Detects subtle proxies, algorithmic biases, and disparate impact patterns."""

    def __init__(self):
        self._proxy_patterns = [
            # 1. Algorithmic & Ad Targeting Exclusion
            {
                "category": ViolationCategory.DISPARATE_IMPACT,
                "variable": ProtectedVariable.RACE,
                "law": "Fair Housing Act (42 U.S.C. § 3604(c)) & HUD Digital Ad Precedents",
                "citation": "42 U.S.C. § 3604(c), HUD v. Facebook Settlement",
                "severity": Severity.HIGH,
                "pattern": re.compile(
                    r"\b(exclude\s+(users?|audiences?|demographics?)\s+interested\s+in\s+(african\s+american|hispanic|spanish|black|asian)|"
                    r"negative\s+demographic\s+targeting\s+on\s+race|"
                    r"filter\s+out\s+(spanish\s+speakers|minority\s+interests)\s+from\s+(mortgage|housing|loan)\s+ads?)\b",
                    re.IGNORECASE
                ),
                "explanation": "Excluding social media or digital audiences from seeing housing or loan ads based on cultural or racial affinity violates 42 U.S.C. § 3604(c).",
                "remediation": "Deliver real estate and lending campaigns broadly across general geographic markets without negative demographic exclusions."
            },

            # 2. Blanket 'No Pets' without Assistance Animal Exemption in Leases/Prompts
            {
                "category": ViolationCategory.REASONABLE_ACCOMMODATION_FAILURE,
                "variable": ProtectedVariable.DISABILITY,
                "law": "Fair Housing Amendments Act of 1988 (42 U.S.C. § 3604(f)(3)(B))",
                "citation": "42 U.S.C. § 3604(f)(3)(B)",
                "severity": Severity.MEDIUM,
                "pattern": re.compile(
                    r"\b(strictly\s+no\s+animals\s+of\s+any\s+kind\s+under\s+any\s+circumstances|"
                    r"absolutely\s+no\s+pets\s+or\s+animals\s+allowed\s+no\s+exceptions|"
                    r"no\s+animals\s+permitted\s+period\s+no\s+exceptions)\b",
                    re.IGNORECASE
                ),
                "explanation": "Strict 'no animals under any circumstances / no exceptions' policies fail to acknowledge the mandatory federal exemption for service and emotional support animals.",
                "remediation": "Add an explicit qualification: 'No pets permitted; reasonable accommodations provided for verified assistance and service animals.'"
            },

            # 3. Mortgage Maternity Leave / Pregnancy Discrimination (ECOA / FHA)
            {
                "category": ViolationCategory.CREDIT_MORTGAGE_DISPARATE_TREATMENT,
                "variable": ProtectedVariable.FAMILIAL_STATUS,
                "law": "Equal Credit Opportunity Act (15 U.S.C. § 1691) & FHA (42 U.S.C. § 3605)",
                "citation": "15 U.S.C. § 1691(a), 42 U.S.C. § 3605",
                "severity": Severity.HIGH,
                "pattern": re.compile(
                    r"\b(discount\s+income\s+due\s+to\s+maternity\s+leave|"
                    r"pause\s+loan\s+approval\s+until\s+borrower\s+returns\s+from\s+maternity\s+leave|"
                    r"require\s+proof\s+of\s+return\s+to\s+work\s+after\s+childbirth\s+before\s+closing|"
                    r"inquire\s+whether\s+borrower\s+is\s+pregnant\s+or\s+plans\s+to\s+have\s+children)\b",
                    re.IGNORECASE
                ),
                "explanation": "Underwriting loans differently due to maternity leave, pregnancy, or family planning inquiries violates ECOA and FHA sex and familial status protections.",
                "remediation": "Treat regular employment income during planned maternity leave as ongoing if the borrower intends to resume employment, without requiring medical disclosures."
            },

            # 4. Crime-Free Lease / Automatic Eviction on Arrest (HUD Disparate Impact)
            {
                "category": ViolationCategory.DISPARATE_IMPACT,
                "variable": ProtectedVariable.CRIMINAL_HISTORY,
                "law": "HUD 2016 Criminal Records Guidance & Texas Dept. of Housing v. Inclusive Communities",
                "citation": "HUD 2016 Guidance, 576 U.S. 519",
                "severity": Severity.HIGH,
                "pattern": re.compile(
                    r"\b(evict\s+tenant\s+immediately\s+upon\s+(any\s+)?arrest|"
                    r"terminate\s+lease\s+if\s+tenant\s+is\s+arrested\s+regardless\s+of\s+guilt|"
                    r"crime[- ]free\s+ordinance\s+mandating\s+eviction\s+without\s+conviction)\b",
                    re.IGNORECASE
                ),
                "explanation": "Automatic eviction or lease cancellation upon arrest without conviction produces an unlawful disparate impact against minority tenants under HUD 2016 guidance.",
                "remediation": "Do not take adverse housing action solely on arrests. Require documented evidence of actual unlawful conduct threatening resident safety."
            },

            # 5. Restrictive Covenants / Deed Restrictions (Shelley v. Kraemer)
            {
                "category": ViolationCategory.RESTRICTIVE_COVENANTS_OR_ZONING,
                "variable": ProtectedVariable.RACE,
                "law": "Shelley v. Kraemer (334 U.S. 1) & Civil Rights Act of 1866",
                "citation": "334 U.S. 1, 42 U.S.C. § 1982",
                "severity": Severity.CRITICAL,
                "pattern": re.compile(
                    r"\b(racially\s+restrictive\s+covenants?|deed\s+restriction\s+prohibiting\s+minorities|"
                    r"covenant\s+stipulating\s+caucasian\s+ownership|property\s+cannot\s+be\s+sold\s+to\s+non[- ]whites)\b",
                    re.IGNORECASE
                ),
                "explanation": "Racially restrictive covenants are unconstitutional and legally void under Shelley v. Kraemer and federal civil rights statutes.",
                "remediation": "Deed restrictions based on race or ethnicity are void as a matter of law and must be stricken entirely."
            },

            # 6. Subtle Steering by Coded Demographics
            {
                "category": ViolationCategory.STEERING,
                "variable": ProtectedVariable.RACE,
                "law": "Fair Housing Act (42 U.S.C. § 3604(a))",
                "citation": "42 U.S.C. § 3604(a)",
                "severity": Severity.HIGH,
                "pattern": re.compile(
                    r"\b(safe\s+white\s+suburb|homogeneous\s+demographic\s+neighborhood|"
                    r"stay\s+away\s+from\s+the\s+ghetto|too\s+many\s+minorities\s+moving\s+in|"
                    r"recommend\s+areas\s+with\s+people\s+like\s+them)\b",
                    re.IGNORECASE
                ),
                "explanation": "Recommending or discouraging properties based on racial or demographic homogeneity constitutes prohibited racial steering under Section 3604(a).",
                "remediation": "Direct clients based on requested budget, square footage, architectural style, and requested school district boundaries without commenting on resident racial makeup."
            }
        ]

    def scan(self, text: str) -> List[ViolationItem]:
        """Scan text for subtle proxy and disparate impact violations."""
        violations: List[ViolationItem] = []
        for item in self._proxy_patterns:
            match = item["pattern"].search(text)
            if match:
                violations.append(
                    ViolationItem(
                        category=item["category"],
                        law_cited=item["law"],
                        statutory_reference=item["citation"],
                        protected_variable=item["variable"],
                        flagged_text=match.group(0),
                        severity=item["severity"],
                        explanation=item["explanation"],
                        remediation_guidance=item["remediation"]
                    )
                )
        return violations
