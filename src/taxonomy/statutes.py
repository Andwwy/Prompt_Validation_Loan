"""
Statutory rules, legal precedents, and regulatory references
governing housing and credit discrimination in the United States.
Derived from: https://en.wikipedia.org/wiki/Housing_discrimination_in_the_United_States
"""

from typing import Dict, Any, List

STATUTORY_FRAMEWORK: Dict[str, Dict[str, Any]] = {
    "CRA_1866": {
        "title": "Civil Rights Act of 1866",
        "citation": "42 U.S.C. § 1982",
        "description": "Guarantees all citizens the same right to inherit, purchase, lease, sell, hold, and convey real and personal property, regardless of race or color.",
        "applies_to": ["race", "color"],
        "key_mechanisms": ["Refusal to sell or lease", "Discriminatory property covenants"],
    },
    "FHA_1968": {
        "title": "Fair Housing Act (Title VIII of the Civil Rights Act of 1968)",
        "citation": "42 U.S.C. §§ 3601-3619",
        "sections": {
            "3604(a)": "Unlawful to refuse to sell or rent or negotiate after the making of a bona fide offer, or to otherwise make unavailable, a dwelling based on protected class.",
            "3604(b)": "Unlawful to discriminate against any person in the terms, conditions, or privileges of sale or rental of a dwelling, or in the provision of services or facilities.",
            "3604(c)": "Unlawful to make, print, or publish, or cause to be made, printed, or published any notice, statement, or advertisement with respect to the sale or rental of a dwelling that indicates any preference, limitation, or discrimination based on protected classes.",
            "3604(d)": "Unlawful to represent to any person because of protected class that any dwelling is not available for inspection, sale, or rental when such dwelling is in fact so available.",
            "3604(e)": "Unlawful to induce or attempt to induce any person to sell or rent any dwelling by representations regarding the entry or prospective entry into the neighborhood of a person of a particular protected class (Blockbusting / Panic Peddling).",
            "3605": "Unlawful for any person or entity engaging in residential real estate-related transactions (mortgage lending, appraisals, brokering) to discriminate based on protected class."
        },
        "applies_to": ["race", "color", "religion", "sex", "national_origin", "familial_status", "disability"],
    },
    "FHAA_1988": {
        "title": "Fair Housing Amendments Act of 1988",
        "citation": "42 U.S.C. § 3604(f)",
        "description": "Expanded the Fair Housing Act to prohibit discrimination based on disability (handicap) and familial status.",
        "requirements": [
            "Reasonable Accommodations: Landlords must make reasonable changes in rules, policies, or practices (e.g., waiving 'no pets' for service animals, emotional support animals, assistance animals; assigning priority accessible parking).",
            "Reasonable Modifications: Tenants with disabilities have the right to make reasonable structural modifications at their expense (e.g., grab bars, ramps, widening doorways).",
            "Accessibility Mandate: Multifamily housing designed and constructed for first occupancy after March 13, 1991 (4+ units) must meet accessibility standards.",
            "Familial Status Protections: Protects families with children under 18, pregnant women, and legal custodians. Restricts 'adults only' policies unless verified as qualifying senior housing (HOPA 55+)."
        ],
        "applies_to": ["disability", "familial_status"]
    },
    "ECOA_1974": {
        "title": "Equal Credit Opportunity Act",
        "citation": "15 U.S.C. § 1691 et seq. (12 C.F.R. Part 1002 - Regulation B)",
        "description": "Prohibits creditors from discriminating against any applicant with respect to any aspect of a credit transaction (mortgages, personal loans, refinancing).",
        "prohibited_bases": [
            "race", "color", "religion", "national_origin", "sex",
            "marital_status", "age", "receipt_of_public_assistance"
        ],
        "key_rules": [
            "Creditors cannot discount or refuse to consider public assistance income (e.g. Section 8, SSDI, TANF, SSI, child support, alimony).",
            "Creditors cannot require a spouse's signature if applicant qualifies individually.",
            "Creditors cannot inquire about birth control, childbearing plans, or family planning."
        ]
    },
    "CRA_1977": {
        "title": "Community Reinvestment Act",
        "citation": "12 U.S.C. § 2901 et seq.",
        "description": "Enacted to combat systemic redlining by requiring commercial banks and savings institutions to help meet credit needs of all segments of their communities, including low- and moderate-income neighborhoods.",
        "applies_to": ["geographic_redlining"]
    },
    "HMDA_1975": {
        "title": "Home Mortgage Disclosure Act",
        "citation": "12 U.S.C. § 2801 et seq. (Regulation C)",
        "description": "Mandates public disclosure of mortgage lending data to expose discriminatory lending practices, loan approval disparities, and redlining patterns.",
        "applies_to": ["geographic_redlining", "race", "national_origin"]
    },
    "LANDMARK_PRECEDENTS": {
        "Buchanan_v_Warley_1917": {
            "case": "Buchanan v. Warley, 245 U.S. 60 (1917)",
            "principle": "Supreme Court unanimously struck down municipal racial zoning ordinances prohibiting African-Americans from occupying or purchasing homes in majority-white blocks as violative of the 14th Amendment."
        },
        "Shelley_v_Kraemer_1948": {
            "case": "Shelley v. Kraemer, 334 U.S. 1 (1948)",
            "principle": "Supreme Court held that state court judicial enforcement of racially restrictive private covenants violates the Equal Protection Clause of the 14th Amendment."
        },
        "Inclusive_Communities_2015": {
            "case": "Texas Dept. of Housing & Community Affairs v. Inclusive Communities Project, 576 U.S. 519 (2015)",
            "principle": "Affirmed that Disparate Impact claims are cognizable under the Fair Housing Act. Policies that are facially neutral but cause arbitrary disproportionate exclusion of protected classes without legitimate necessity violate the FHA."
        }
    },
    "HUD_ADMIN_GUIDANCE": {
        "HUD_2016_CRIMINAL_RECORDS": {
            "title": "HUD Office of General Counsel Guidance on Criminal Records (2016)",
            "rule": "Blanket exclusions of applicants based on criminal history have an unlawful disparate impact on Black and Hispanic individuals. Arrest records alone cannot justify housing denial (an arrest does not equal guilt). Policies must conduct individualized reviews considering nature of crime and time elapsed."
        },
        "HUD_2016_LEP": {
            "title": "HUD Guidance on Limited English Proficiency (2016)",
            "rule": "Exclusionary policies targeting individuals with Limited English Proficiency (LEP) or imposing English-only rules violate FHA provisions against National Origin discrimination."
        },
        "HUD_2021_EQUAL_ACCESS": {
            "title": "HUD Executive Order & Bostock Guidance on LGBTQ+ Protections (2021)",
            "rule": "Under the Supreme Court precedent Bostock v. Clayton County, prohibition of sex discrimination under the Fair Housing Act encompasses discrimination based on Sexual Orientation and Gender Identity."
        },
        "HUD_DIGITAL_AD_TARGETING": {
            "title": "HUD Algorithmic & Ad Targeting Rules (e.g. HUD v. Facebook settlement)",
            "rule": "Using micro-targeting, lookalike models, or demographic/geographic exclusion tools to prevent protected classes from seeing housing or mortgage advertisements violates 42 U.S.C. § 3604(c)."
        }
    }
}
