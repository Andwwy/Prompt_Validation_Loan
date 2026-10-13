"""
Taxonomy of Protected Variables, Proxies, and Demographic Indicators.
"""

from typing import Dict, List, Any
from src.models import ProtectedVariable

PROTECTED_VARIABLES_CONFIG: Dict[ProtectedVariable, Dict[str, Any]] = {
    ProtectedVariable.RACE: {
        "label": "Race & Color",
        "statutes": ["Civil Rights Act of 1866 (42 U.S.C. § 1982)", "Fair Housing Act (42 U.S.C. § 3604)", "ECOA (15 U.S.C. § 1691)"],
        "keywords": [
            "white", "caucasian", "black", "african american", "asian",
            "hispanic", "latino", "latina", "native american", "indigenous",
            "biracial", "multiracial", "colored", "oriental"
        ],
        "coded_proxies": [
            "good neighborhood demographics", "culturally homogeneous",
            "urban crowd", "ghetto", "inner city element", "traditional demographics",
            "changing neighborhood", "undesirable demographic", "white neighborhood"
        ]
    },
    ProtectedVariable.RELIGION: {
        "label": "Religion & Creed",
        "statutes": ["Fair Housing Act (42 U.S.C. § 3604)", "ECOA (15 U.S.C. § 1691)"],
        "keywords": [
            "christian", "catholic", "protestant", "jewish", "jew", "muslim",
            "islamic", "hindu", "buddhist", "mormon", "atheist", "mosque",
            "synagogue", "church goer", "god-fearing", "christian community"
        ],
        "coded_proxies": [
            "traditional faith values", "near the church only", "kosher neighborhood only",
            "bible study members", "parish community"
        ]
    },
    ProtectedVariable.NATIONAL_ORIGIN: {
        "label": "National Origin & Ancestry",
        "statutes": ["Fair Housing Act (42 U.S.C. § 3604)", "ECOA (15 U.S.C. § 1691)", "HUD 2016 Guidance"],
        "keywords": [
            "immigrant", "foreign-born", "mexican", "chinese", "indian", "middle eastern",
            "african", "european", "citizens only", "us born only", "american born"
        ],
        "coded_proxies": [
            "real americans", "native born", "non-citizens barred", "foreign accent",
            "must have us passport"
        ]
    },
    ProtectedVariable.LANGUAGE_PROFICIENCY: {
        "label": "Limited English Proficiency (Proxy for National Origin)",
        "statutes": ["HUD 2016 Guidance on Limited English Proficiency", "Fair Housing Act (42 U.S.C. § 3604)"],
        "keywords": [
            "english only", "fluent english required", "must speak english",
            "no spanish speakers", "broken english", "accented speech"
        ],
        "coded_proxies": [
            "must converse in clear native english", "english language preference"
        ]
    },
    ProtectedVariable.SEX: {
        "label": "Sex & Gender",
        "statutes": ["Fair Housing Act (42 U.S.C. § 3604)", "ECOA (15 U.S.C. § 1691)", "VAWA"],
        "keywords": [
            "male only", "female only", "men only", "women only", "gentlemen only",
            "ladies only", "bachelor only", "single woman"
        ],
        "coded_proxies": [
            "bachelor pad", "female environment", "man cave"
        ]
    },
    ProtectedVariable.SEXUAL_ORIENTATION: {
        "label": "Sexual Orientation",
        "statutes": ["Fair Housing Act (HUD 2021 Guidance under Bostock v. Clayton County)"],
        "keywords": [
            "gay", "lesbian", "bisexual", "homosexual", "queer", "straight only",
            "heterosexual couple only", "traditional marriage only"
        ],
        "coded_proxies": [
            "traditional family values only", "biblical marriage only"
        ]
    },
    ProtectedVariable.GENDER_IDENTITY: {
        "label": "Gender Identity",
        "statutes": ["Fair Housing Act (HUD 2021 Guidance under Bostock v. Clayton County)"],
        "keywords": [
            "transgender", "trans", "non-binary", "gender non-conforming",
            "biological female only", "biological male only", "cisgender only"
        ],
        "coded_proxies": [
            "birth gender only", "natural born sex"
        ]
    },
    ProtectedVariable.FAMILIAL_STATUS: {
        "label": "Familial Status (Children under 18, Pregnancy, Custody)",
        "statutes": ["Fair Housing Amendments Act of 1988 (42 U.S.C. § 3604)", "ECOA (15 U.S.C. § 1691)"],
        "keywords": [
            "no children", "no kids", "adults only", "mature adults", "no toddlers",
            "no babies", "child-free", "singles only", "empty nesters preferred",
            "pregnant", "expecting mothers", "no strollers"
        ],
        "coded_proxies": [
            "quiet professional couple only", "not suitable for children",
            "perfect for single bachelor", "strictly adult living"
        ]
    },
    ProtectedVariable.DISABILITY: {
        "label": "Disability & Handicap (Physical, Mental, Sensory)",
        "statutes": ["Fair Housing Amendments Act of 1988 (42 U.S.C. § 3604(f))"],
        "keywords": [
            "wheelchair", "handicapped", "disabled", "autism", "blind", "deaf",
            "mental illness", "service animal", "assistance animal", "guide dog",
            "emotional support animal", "esa", "no therapy animals", "able-bodied only"
        ],
        "coded_proxies": [
            "must be able to walk up stairs independently", "no medical equipment",
            "strict no pets policy including support dogs", "no mobility scooters"
        ]
    },
    ProtectedVariable.MARITAL_STATUS: {
        "label": "Marital Status (Credit & Lending Protection)",
        "statutes": ["Equal Credit Opportunity Act (15 U.S.C. § 1691 - Regulation B)"],
        "keywords": [
            "married couple only", "unmarried", "single mother", "divorced",
            "separated", "spouse co-sign required", "unwed"
        ],
        "coded_proxies": [
            "traditional married households only", "husband must sign"
        ]
    },
    ProtectedVariable.AGE: {
        "label": "Age (Lending & Credit Protection)",
        "statutes": ["Equal Credit Opportunity Act (15 U.S.C. § 1691)"],
        "keywords": [
            "too old for loan", "elderly applicant risk", "over 65 lending risk",
            "young borrowers barred", "maximum age limit for mortgage"
        ],
        "coded_proxies": [
            "life expectancy loan cut-off", "approaching retirement age penalty"
        ]
    },
    ProtectedVariable.SOURCE_OF_INCOME: {
        "label": "Source of Income / Public Assistance",
        "statutes": ["ECOA (15 U.S.C. § 1691)", "State Fair Housing Laws", "HUD Disparate Impact"],
        "keywords": [
            "section 8", "housing choice voucher", "welfare", "ssdi", "ssi",
            "food stamps", "snap", "tanf", "public assistance", "alimony", "child support"
        ],
        "coded_proxies": [
            "no vouchers", "no government assistance", "employed earned income only",
            "w2 income only", "must work 40 hours a week"
        ]
    },
    ProtectedVariable.CRIMINAL_HISTORY: {
        "label": "Criminal History & Arrest Records",
        "statutes": ["HUD 2016 Guidance on Criminal Records", "Inclusive Communities Disparate Impact"],
        "keywords": [
            "no arrest record", "clean record required", "any arrest disqualifies",
            "no criminal background ever", "lifetime felony ban"
        ],
        "coded_proxies": [
            "zero tolerance for any police interaction", "must pass police background check without any arrests"
        ]
    },
    ProtectedVariable.GEOGRAPHIC_LOCATION: {
        "label": "Geographic Redlining & Neighborhood Bias",
        "statutes": ["Community Reinvestment Act (12 U.S.C. § 2901)", "FHA (42 U.S.C. § 3605)", "HMDA"],
        "keywords": [
            "redline", "redlined zip code", "high minority zip code", "bad neighborhood",
            "avoid inner city loans", "suburban loans only", "steer to minority area"
        ],
        "coded_proxies": [
            "exclude inner-city zip codes from mortgage marketing", "blacklist zip codes based on crime/demographics"
        ]
    }
}
