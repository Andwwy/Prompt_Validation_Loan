"""
Automated Pytest Suite executing benchmark validation cases.
"""

import json
import pytest
from pathlib import Path
from src.engine import PromptValidator

BENCHMARK_FILE = Path(__file__).parent / "benchmark_cases.json"


@pytest.fixture
def validator():
    # Test deterministic and heuristic rule engine (without remote API dependency)
    return PromptValidator(gemini_api_key=None)


def test_benchmark_suite(validator):
    with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    passed = 0
    total = len(test_cases)

    for case in test_cases:
        prompt = case["prompt"]
        expected_compliant = case["expected_compliant"]

        result = validator.validate(prompt, enable_semantic=False)

        assert result.is_compliant == expected_compliant, (
            f"Case {case['id']} failed: Expected compliant={expected_compliant}, got {result.is_compliant}. "
            f"Violations: {[v.category.value for v in result.violations]}"
        )

        if not expected_compliant:
            assert len(result.violations) > 0
            assert result.risk_score > 0.0
            assert result.suggested_compliant_prompt is not None

            if case["expected_category"]:
                actual_categories = [v.category.value for v in result.violations]
                assert case["expected_category"] in actual_categories, (
                    f"Case {case['id']}: Expected category '{case['expected_category']}' not in {actual_categories}"
                )
        else:
            assert len(result.violations) == 0
            assert result.risk_score == 0.0

        passed += 1

    print(f"\nAll {passed}/{total} benchmark validation test cases passed successfully!")
