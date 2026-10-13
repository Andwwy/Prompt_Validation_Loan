"""
Violation definitions, legal tests, and remediation guidelines
for housing and credit discrimination.
"""

from typing import Dict, Any
from src.models import ViolationCategory, Severity

VIOLATION_DEFINITIONS: Dict[ViolationCategory, Dict[str, Any]] = {
    ViolationCategory.DISCRIMINATORY_ADVERTISING: {
        "title": "Discriminatory Advertising or Notice",
        "primary_law": "Fair Housing Act (42 U.S.C. § 3604(c))",
        "default_severity": Severity.CRITICAL,
        "description": "It is unlawful to make, print, publish, or cause to be published any notice, statement, or advertisement that indicates any preference, limitation, or discrimination based on race, color, religion, sex, handicap, familial status, or national origin.",
        "remediation_rule": "Focus descriptions strictly on physical property features, amenities, and location, never describing ideal tenants, demographics, or excluding protected classes."
    },
    ViolationCategory.STEERING: {
        "title": "Racial or Demographic Steering",
        "primary_law": "Fair Housing Act (42 U.S.C. § 3604(a)) & Havens Realty Corp. v. Coleman",
        "default_severity": Severity.HIGH,
        "description": "Steering occurs when housing providers, agents, or algorithms guide homeseekers toward or away from specific neighborhoods or buildings based on their race, ethnicity, or other protected traits.",
        "remediation_rule": "Present all available housing choices matching the client's objective physical, financial, and geographic parameters without referencing neighborhood demographics."
    },
    ViolationCategory.REDLINING: {
        "title": "Geographic Redlining & Credit Denial",
        "primary_law": "Fair Housing Act (42 U.S.C. § 3605), ECOA (15 U.S.C. § 1691), CRA (12 U.S.C. § 2901)",
        "default_severity": Severity.CRITICAL,
        "description": "Denying mortgages, personal loans, or insurance, or imposing unfavorable loan terms on properties in specific geographic areas based on the racial or income demographics of the community.",
        "remediation_rule": "Base lending, underwriting, and marketing criteria strictly on individual creditworthiness, debt-to-income, loan-to-value, and objective appraisal metrics without geographic demographic filtering."
    },
    ViolationCategory.REVERSE_REDLINING_PREDATORY: {
        "title": "Reverse Redlining & Predatory Targeting",
        "primary_law": "Fair Housing Act & Equal Credit Opportunity Act",
        "default_severity": Severity.HIGH,
        "description": "Targeting minority or protected communities with exploitative, subprime, higher-interest, or predatory loan products while offering prime rates elsewhere.",
        "remediation_rule": "Ensure uniform loan pricing, APR, and fee schedules based strictly on transparent, non-discriminatory credit risk tiers."
    },
    ViolationCategory.CREDIT_MORTGAGE_DISPARATE_TREATMENT: {
        "title": "Credit & Mortgage Disparate Treatment",
        "primary_law": "Equal Credit Opportunity Act (15 U.S.C. § 1691 / 12 C.F.R. § 1002 - Reg B)",
        "default_severity": Severity.CRITICAL,
        "description": "Treating credit applicants differently based on race, color, religion, national origin, sex, marital status, age, or public assistance income.",
        "remediation_rule": "Apply neutral underwriting benchmarks uniformly across all applicants without inquiring about or discounting protected variables."
    },
    ViolationCategory.DISPARATE_IMPACT: {
        "title": "Facially Neutral Disparate Impact",
        "primary_law": "Texas Dept. of Housing v. Inclusive Communities Project (576 U.S. 519)",
        "default_severity": Severity.HIGH,
        "description": "Practices that appear neutral on their face but have a disproportionate, unjustified adverse impact on a protected class and cannot be justified by substantial, legitimate business necessity.",
        "remediation_rule": "Evaluate whether the business objective can be achieved through less restrictive, non-discriminatory alternative criteria."
    },
    ViolationCategory.REASONABLE_ACCOMMODATION_FAILURE: {
        "title": "Refusal of Reasonable Accommodation",
        "primary_law": "Fair Housing Amendments Act of 1988 (42 U.S.C. § 3604(f)(3)(B))",
        "default_severity": Severity.CRITICAL,
        "description": "Refusal to make reasonable changes in rules, policies, practices, or services when necessary to afford an individual with a disability an equal opportunity to use and enjoy a dwelling (e.g. assistance animals, assigned accessible parking).",
        "remediation_rule": "Explicitly state that assistance animals (service animals and emotional support animals) are exempt from pet policies and pet deposit fees."
    },
    ViolationCategory.REASONABLE_MODIFICATION_FAILURE: {
        "title": "Refusal of Reasonable Modification",
        "primary_law": "Fair Housing Amendments Act of 1988 (42 U.S.C. § 3604(f)(3)(A))",
        "default_severity": Severity.HIGH,
        "description": "Refusal to permit a person with a disability to make reasonable physical modifications to existing premises at their expense if necessary for full enjoyment of the premises.",
        "remediation_rule": "Permit reasonable structural modifications (ramps, grab bars, lowered switches) subject to reasonable safety and restoration terms."
    },
    ViolationCategory.RESTRICTIVE_COVENANTS_OR_ZONING: {
        "title": "Restrictive Covenants & Exclusionary Filtering",
        "primary_law": "Shelley v. Kraemer (334 U.S. 1) & Buchanan v. Warley (245 U.S. 60)",
        "default_severity": Severity.CRITICAL,
        "description": "Using or enforcing private deed restrictions or exclusionary algorithmic filters that exclude protected groups.",
        "remediation_rule": "Eliminate all demographic and race-based restrictions or neighborhood segregation proxies from prompts and systems."
    },
    ViolationCategory.SOURCE_OF_INCOME_EXCLUSION: {
        "title": "Source of Income & Voucher Exclusion",
        "primary_law": "ECOA (15 U.S.C. § 1691(a)(2)) & State/Local Fair Housing Laws",
        "default_severity": Severity.MEDIUM,
        "description": "Refusing applicants solely because their income is derived from public assistance, Section 8 Housing Choice Vouchers, SSDI, alimony, or child support.",
        "remediation_rule": "Evaluate affordability based on total verified income from all lawful sources or compare the applicant's tenant-share of rent against income standards."
    },
    ViolationCategory.CRIMINAL_HISTORY_BLANKET_EXCLUSION: {
        "title": "Blanket Criminal Record Exclusion",
        "primary_law": "HUD 2016 Guidance on Criminal Records under the Fair Housing Act",
        "default_severity": Severity.MEDIUM,
        "description": "Disqualifying applicants based on arrest records (which do not prove guilt) or imposing blanket lifetime bans for any conviction without considering severity and time elapsed.",
        "remediation_rule": "Replace blanket bans with individualized review of convictions only (excluding arrests), weighing the nature of the crime and elapsed time against direct threat to safety."
    },
    ViolationCategory.LANGUAGE_LEP_EXCLUSION: {
        "title": "Limited English Proficiency (LEP) Exclusion",
        "primary_law": "HUD 2016 Guidance on Limited English Proficiency & FHA National Origin",
        "default_severity": Severity.HIGH,
        "description": "Excluding applicants who are not fluent in English or mandating English-only communication as a condition of housing or credit.",
        "remediation_rule": "Accept qualified applicants regardless of primary language; provide translated materials or permit third-party interpreters."
    },
    ViolationCategory.HARASSMENT_QUID_PRO_QUO: {
        "title": "Harassment & Quid Pro Quo Coercion",
        "primary_law": "Fair Housing Act (42 U.S.C. § 3617) & HUD Harassment Rule",
        "default_severity": Severity.CRITICAL,
        "description": "Subjecting tenants or applicants to severe or pervasive discriminatory harassment or conditioning housing/credit terms on sexual favors or personal submission.",
        "remediation_rule": "Maintain strict non-harassment policies and professional terms of interaction."
    }
}
