from pathlib import Path

from dialectica_reasoning.library import load_curated_library


def test_curated_library_loads_all_prompt_two_questions() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    library = load_curated_library(repo_root / "data" / "seed" / "reasoning_library.json")

    assert len(library) == 23
    assert set(library) >= {"R-1", "R-8", "W-1", "W-7", "S-1", "S-8"}
    assert library["S-1"].counterfactual_supported is True
    assert library["R-6"].similarity_supported is True
    assert library["W-6"].primary_framework == "pattern_matching"
