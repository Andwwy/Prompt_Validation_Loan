"""
Deterministic Rule & Heuristic Scanner for housing and lending discrimination.
Executes sub-millisecond pattern checks for explicit violations and statutory provisions.
"""

import re
from typing import List, Tuple
from src.models import ViolationItem, ViolationCategory, ProtectedVariable, Severity
from src.taxonomy.violations import VIOLATION_DEFINITIONS


class RuleScanner:
    """Fast-path deterministic regex scanner for explicit housing & credit violations."""

    def __init__(self):
        self._rules = self._compile_rules()

    def _compile_rules(self) -> List[dict]:
        return [
            # 1. FAMILIAL STATUS (FHA / FHAA 1988)
            {
                "id": "RULE_FAMILIAL_NO_KIDS",
                "category": ViolationCategory.DISCRIMINATORY_ADVERTISING,
                "variable": ProtectedVariable.FAMILIAL_STATUS,
                "law": "Fair Housing Act (42 U.S.C. § 3604(c)) & FHAA 1988",
                "citation": "42 U.S.C. § 3604(c)",
                "severity": Severity.CRITICAL,
                "pattern": re.compile(
                    r"\b(no\s+(children|kids|babies|toddlers|strollers)|adults\s+only|child[- ]free|strictly\s+adults|"
                    r"not\s+suitable\s+for\s+(children|kids|families)|mature\s+(adults|singles|couples)\s+only|"
                    r"no\s+young\s+children|couples\s+without\s+children|empty\s+nesters\s+preferred|"
                    r"perfect\s+for\s+(a\s+)?(single\s+(quiet\s+)?professional|bachelor)|ideal\s+for\s+childless)\b",
                    re.IGNORECASE
                ),
                "explanation": "Expressing preference against families with children under 18 or indicating 'adults only' unlawfully discriminates based on familial status under the Fair Housing Act.",
                "remediation": "Describe the physical property attributes (e.g. '2-bedroom quiet condo') rather than specifying preferred tenant family composition."
            },

            # 2. RELIGIOUS DISCRIMINATION (FHA / ECOA)
            {
                "id": "RULE_RELIGION_PREFERENCE",
                "category": ViolationCategory.DISCRIMINATORY_ADVERTISING,
                "variable": ProtectedVariable.RELIGION,
                "law": "Fair Housing Act (42 U.S.C. § 3604(c))",
                "citation": "42 U.S.C. § 3604(c)",
                "severity": Severity.CRITICAL,
                "pattern": re.compile(
                    r"\b((christian|jewish|catholic|protestant|muslim|islamic|mormon|hindu)\s+(only|preferred|community|values|tenants|homeowners)|"
                    r"church[- ]go(ers|ing)\s+(only|preferred)|god[- ]fearing\s+(only|preferred|tenants)|"
                    r"near\s+(the\s+)?(church|mosque|synagogue)\s+for\s+(believers|fellow\s+christians))\b",
                    re.IGNORECASE
                ),
                "explanation": "Advertising preferences based on religion, creed, or faith affiliation violates federal fair housing advertising mandates.",
                "remediation": "Remove all religious references and state that housing is available to all qualified applicants without religious criteria."
            },

            # 3. RACE & ETHNIC EXCLUSION (FHA / CRA 1866)
            {
                "id": "RULE_RACE_EXPLICIT",
                "category": ViolationCategory.DISCRIMINATORY_ADVERTISING,
                "variable": ProtectedVariable.RACE,
                "law": "Fair Housing Act (42 U.S.C. § 3604(c)) & Civil Rights Act of 1866 (42 U.S.C. § 1982)",
                "citation": "42 U.S.C. § 1982, § 3604(c)",
                "severity": Severity.CRITICAL,
                "pattern": re.compile(
                    r"\b((white|caucasian|black|african\s+american|asian|hispanic|latino)\s+(only|preferred|tenants|residents)|"
                    r"no\s+(blacks|african\s+americans|whites|asians|hispanics|minorities)|"
                    r"(traditional|white)\s+neighborhood\s+demographics|avoid\s+(minority|black|hispanic)\s+neighborhoods)\b",
                    re.IGNORECASE
                ),
                "explanation": "Expressing any racial preference, limitation, or exclusion is a direct violation of Title VIII of the Civil Rights Act and 42 U.S.C. § 1982.",
                "remediation": "Do not mention or filter by race, color, or demographic traits under any circumstances."
            },

            # 4. NATIONAL ORIGIN & LANGUAGE (HUD 2016 LEP Guidance / FHA)
            {
                "id": "RULE_NATIONAL_ORIGIN_LANGUAGE",
                "category": ViolationCategory.LANGUAGE_LEP_EXCLUSION,
                "variable": ProtectedVariable.LANGUAGE_PROFICIENCY,
                "law": "HUD 2016 Guidance on Limited English Proficiency & FHA (42 U.S.C. § 3604)",
                "citation": "42 U.S.C. § 3604, HUD 2016 LEP Guidance",
                "severity": Severity.HIGH,
                "pattern": re.compile(
                    r"\b(english\s+only|must\s+speak\s+(fluent\s+)?english|fluent\s+english\s+speakers?\s+only|"
                    r"no\s+spanish\s+speakers|english\s+speaking\s+tenants?\s+only|us\s+born\s+citizens?\s+only|"
                    r"citizens\s+only|native\s+born\s+americans?\s+only|american\s+born\s+only)\b",
                    re.IGNORECASE
                ),
                "explanation": "Mandating English fluency or excluding non-English speakers operates as an unlawful proxy for national origin discrimination under HUD guidance and the Fair Housing Act.",
                "remediation": "Remove language proficiency restrictions. Allow applicants to use translators or provide standard translated documentation."
            },

            # 5. DISABILITY & ASSISTANCE ANIMALS (FHAA 1988)
            {
                "id": "RULE_DISABILITY_SERVICE_ANIMAL",
                "category": ViolationCategory.REASONABLE_ACCOMMODATION_FAILURE,
                "variable": ProtectedVariable.DISABILITY,
                "law": "Fair Housing Amendments Act of 1988 (42 U.S.C. § 3604(f)(3)(B))",
                "citation": "42 U.S.C. § 3604(f)(3)(B)",
                "severity": Severity.CRITICAL,
                "pattern": re.compile(
                    r"\b(no\s+(service|assistance|therapy|guide|support)\s+animals?|"
                    r"no\s+emotional\s+support\s+animals?|no\s+esas?|"
                    r"no[- ]pets?(\s+policy)?\s+.*?(including|enforced\s+against|applied\s+to)\s+.*?(service|support|assistance)\s+animals|"
                    r"pet\s+fee\s+for\s+(service|assistance|support)\s+animals?|no\s+seeing\s+eye\s+dogs)\b",
                    re.IGNORECASE
                ),
                "explanation": "Refusing service animals or assistance animals, or imposing pet fees on them, constitutes unlawful denial of a reasonable accommodation under the Fair Housing Act.",
                "remediation": "Clarify that assistance animals and service animals are exempt from pet prohibitions and pet fees as mandated by FHAA."
            },

            # 6. DISABILITY MODIFICATIONS / MOBILITY
            {
                "id": "RULE_DISABILITY_MODIFICATIONS",
                "category": ViolationCategory.REASONABLE_MODIFICATION_FAILURE,
                "variable": ProtectedVariable.DISABILITY,
                "law": "Fair Housing Amendments Act of 1988 (42 U.S.C. § 3604(f)(3)(A))",
                "citation": "42 U.S.C. § 3604(f)(3)(A)",
                "severity": Severity.HIGH,
                "pattern": re.compile(
                    r"\b(no\s+(wheelchairs|wheelchair\s+ramps|grab\s+bars)|"
                    r"refus(e|ing|ed|al\s+of)\s+(to\s+install|permission\s+for)?\s*(a\s+)?(ramp|grab\s+bar|wheelchair\s+access)|"
                    r"able[- ]bodied\s+(tenants|residents|applicants)\s+only|"
                    r"must\s+be\s+able\s+to\s+walk\s+stairs\s+without\s+assistance)\b",
                    re.IGNORECASE
                ),
                "explanation": "Refusing to permit reasonable physical modifications (such as wheelchair ramps or grab bars) violates Section 3604(f)(3)(A) of the Fair Housing Act.",
                "remediation": "Permit reasonable modifications to allow equal access, subject to standard restoration agreements where applicable."
            },

            # 7. SOURCE OF INCOME & SECTION 8 VOUCHERS (ECOA / Disparate Impact)
            {
                "id": "RULE_SOURCE_OF_INCOME_VOUCHER",
                "category": ViolationCategory.SOURCE_OF_INCOME_EXCLUSION,
                "variable": ProtectedVariable.SOURCE_OF_INCOME,
                "law": "Equal Credit Opportunity Act (15 U.S.C. § 1691(a)(2)) & State Fair Housing Protections",
                "citation": "15 U.S.C. § 1691(a)(2)",
                "severity": Severity.MEDIUM,
                "pattern": re.compile(
                    r"\b(no\s+section\s+8|no\s+vouchers|section\s+8\s+(is\s+)?not\s+accepted|"
                    r"no\s+housing\s+choice\s+vouchers?|no\s+government\s+(subsidies|assistance|vouchers)|"
                    r"no\s+welfare|w2\s+income\s+only|employed\s+wages\s+only|"
                    r"discount\s+public\s+assistance\s+income|refuse\s+ssdi\s+income)\b",
                    re.IGNORECASE
                ),
                "explanation": "Blanket rejection of Section 8 vouchers or discounting public assistance income violates ECOA lending rules and fair housing statutes, producing an unlawful disparate impact.",
                "remediation": "Screen applicants based on their portion of the rent and evaluate all lawful, verifiable sources of income equally."
            },

            # 8. CRIMINAL HISTORY & ARREST RECORDS (HUD 2016 Guidance)
            {
                "id": "RULE_CRIMINAL_HISTORY_BLANKET",
                "category": ViolationCategory.CRIMINAL_HISTORY_BLANKET_EXCLUSION,
                "variable": ProtectedVariable.CRIMINAL_HISTORY,
                "law": "HUD 2016 Guidance on Criminal Records under the Fair Housing Act",
                "citation": "HUD 2016 Criminal History Guidance",
                "severity": Severity.MEDIUM,
                "pattern": re.compile(
                    r"\b(no\s+arrest\s+records?|clean\s+arrest\s+record\s+required|"
                    r"any\s+arrest\s+disqualifies|zero\s+tolerance\s+for\s+any\s+(arrest|criminal\s+interaction)|"
                    r"blanket\s+ban\s+on\s+all\s+(criminal|felony)\s+records?|"
                    r"never\s+rent\s+to\s+anyone\s+with\s+a\s+criminal\s+record)\b",
                    re.IGNORECASE
                ),
                "explanation": "Denying housing based on arrest records (which do not prove unlawful conduct) or imposing lifetime blanket bans without individualized review violates HUD 2016 Fair Housing guidance.",
                "remediation": "Do not consider arrest records. For convictions, conduct individualized assessments considering the nature, severity, and elapsed time since the offense."
            },

            # 9. MARITAL STATUS & GENDER LENDING (ECOA Reg B)
            {
                "id": "RULE_ECOA_MARITAL_STATUS",
                "category": ViolationCategory.CREDIT_MORTGAGE_DISPARATE_TREATMENT,
                "variable": ProtectedVariable.MARITAL_STATUS,
                "law": "Equal Credit Opportunity Act (15 U.S.C. § 1691 / 12 C.F.R. § 1002 - Reg B)",
                "citation": "15 U.S.C. § 1691(a)(1)",
                "severity": Severity.HIGH,
                "pattern": re.compile(
                    r"\b(married\s+couples?\s+only|unmarried\s+applicants?\s+(are\s+)?(not\s+eligible|denied)|"
                    r"husband\s+must\s+(co-?sign|sign)|spouse\s+must\s+co-?sign\s+regardless|"
                    r"single\s+(mothers?|women)\s+require\s+(a\s+)?male\s+guarantor|male\s+guarantor|"
                    r"penalize\s+unmarried\s+status|inquire\s+about\s+(birth\s+control|childbearing\s+plans))\b",
                    re.IGNORECASE
                ),
                "explanation": "Treating credit or housing applicants differently based on marital status or requiring spousal co-signatures when an applicant qualifies individually violates ECOA Regulation B.",
                "remediation": "Apply standard credit and debt-to-income benchmarks regardless of applicant marital status or household composition."
            },

            # 10. SEXUAL ORIENTATION & GENDER IDENTITY (Bostock Precedent & HUD 2021)
            {
                "id": "RULE_LGBTQ_DISCRIMINATION",
                "category": ViolationCategory.DISCRIMINATORY_ADVERTISING,
                "variable": ProtectedVariable.SEXUAL_ORIENTATION,
                "law": "Fair Housing Act (HUD 2021 Guidance under Bostock v. Clayton County)",
                "citation": "42 U.S.C. § 3604(c), HUD Bostock Memo",
                "severity": Severity.CRITICAL,
                "pattern": re.compile(
                    r"\b(straight\s+couples?\s+only|heterosexuals?\s+only|no\s+(gay|lesbian|homosexual|lgbtq|transgender)\s+(tenants?|couples?|borrowers?)|"
                    r"biological\s+(males?|females?)\s+only|natural[- ]born\s+sex\s+only|"
                    r"traditional\s+marriage\s+between\s+man\s+and\s+woman\s+only)\b",
                    re.IGNORECASE
                ),
                "explanation": "Discrimination against LGBTQ+ individuals violates the Fair Housing Act's sex discrimination prohibition under federal judicial and HUD enforcement standards.",
                "remediation": "Remove all references to sexual orientation, gender identity, or marital definition."
            },

            # 11. REDLINING & GEOGRAPHIC EXCLUSION (CRA / HMDA / FHA 3605)
            {
                "id": "RULE_REDLINING_EXPLICIT",
                "category": ViolationCategory.REDLINING,
                "variable": ProtectedVariable.GEOGRAPHIC_LOCATION,
                "law": "Community Reinvestment Act (12 U.S.C. § 2901) & Fair Housing Act (42 U.S.C. § 3605)",
                "citation": "12 U.S.C. § 2901, 42 U.S.C. § 3605",
                "severity": Severity.CRITICAL,
                "pattern": re.compile(
                    r"\b(redline\s+(this|the|those)\s+(zip\s+codes?|neighborhoods?|areas?)|"
                    r"do\s+not\s+(lend|offer\s+mortgages|market\s+loans)\s+in\s+.*?(black|hispanic|minority|inner[- ]city)\s+.*?(neighborhoods?|zip\s+codes?)|"
                    r"exclude\s+.*?(minority|low[- ]income|inner[- ]city)\s+.*?(zip\s+codes?|neighborhoods?)\s+from\s+.*?(marketing|underwriting|pre-?approvals?|mortgage|loans?)|"
                    r"blacklist\s+zip\s+codes?\s+due\s+to\s+demographics)\b",
                    re.IGNORECASE
                ),
                "explanation": "Restricting loans or marketing based on geographic demographics is illegal redlining under the Community Reinvestment Act and Fair Housing Act.",
                "remediation": "Offer lending and housing services across entire service areas without geographic or demographic exclusions."
            },

            # 12. RACIAL STEERING (Havens Realty Corp. v. Coleman)
            {
                "id": "RULE_STEERING_EXPLICIT",
                "category": ViolationCategory.STEERING,
                "variable": ProtectedVariable.RACE,
                "law": "Fair Housing Act (42 U.S.C. § 3604(a)) & Havens Realty Corp. v. Coleman",
                "citation": "42 U.S.C. § 3604(a)",
                "severity": Severity.HIGH,
                "pattern": re.compile(
                    r"\b(steer\s+.*?(buyers?|clients?|renters?)|"
                    r"(live|rent|buy|reside)\s+(near|among)\s+(other\s+)?(white|black|asian|hispanic)\s+(families|couples|residents|neighbors)|"
                    r"guide\s+minority\s+borrowers?\s+away\s+from\s+white\s+neighborhoods?|"
                    r"show\s+only\s+(white|black|hispanic|asian)\s+neighborhoods?\s+to\s+(this|the)\s+buyer|"
                    r"suggest\s+neighborhoods?\s+with\s+their\s+own\s+kind)\b",
                    re.IGNORECASE
                ),
                "explanation": "Guiding homeseekers toward or away from specific neighborhoods based on racial composition constitutes unlawful racial steering.",
                "remediation": "Provide comprehensive property options tailored solely to buyer price and objective home specifications."
            }
        ]

    def scan(self, text: str) -> List[ViolationItem]:
        """Scan input text against compiled deterministic regex rules."""
        violations: List[ViolationItem] = []
        for rule in self._rules:
            match = rule["pattern"].search(text)
            if match:
                matched_span = match.group(0)
                violations.append(
                    ViolationItem(
                        category=rule["category"],
                        law_cited=rule["law"],
                        statutory_reference=rule["citation"],
                        protected_variable=rule["variable"],
                        flagged_text=matched_span,
                        severity=rule["severity"],
                        explanation=rule["explanation"],
                        remediation_guidance=rule["remediation"]
                    )
                )
        return violations
