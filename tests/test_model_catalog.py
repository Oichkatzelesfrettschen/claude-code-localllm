"""Tests for model catalog and VRAM tier coverage."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

CATALOG_PATH = Path(__file__).parents[1] / "tools" / "local_llm" / "model_catalog.json"


@pytest.fixture
def catalog():
    """Load the model catalog."""
    if not CATALOG_PATH.exists():
        pytest.skip("model_catalog.json not found")
    return json.loads(CATALOG_PATH.read_text())


def test_all_tiers_present(catalog):
    """Test that all expected VRAM tiers are defined and no unexpected tiers exist."""
    expected_tiers = {
        "1gb", "2gb", "3gb", "4gb", "6gb", "8gb",
        "10gb", "11gb", "12gb", "16gb", "24gb", "32gb+",
    }
    actual_tiers = {t["tier"] for t in catalog["tiers"]}

    missing = expected_tiers - actual_tiers
    assert not missing, f"Missing tiers: {missing}"

    unexpected = actual_tiers - expected_tiers
    assert not unexpected, f"Unexpected tiers: {unexpected}"


def test_all_tiers_present(catalog):
    """Test that all expected VRAM tiers are defined."""
    expected_tiers = {
        "1gb", "2gb", "3gb", "4gb", "6gb", "8gb",
        "10gb", "11gb", "12gb", "16gb", "24gb", "32gb+",
    }
    actual_tiers = {t["tier"] for t in catalog["tiers"]}

    missing = expected_tiers - actual_tiers
    assert not missing, f"Missing tiers: {missing}"


def test_tiers_have_vram_limits(catalog):
    """Test that all tiers specify VRAM limits."""
    for tier in catalog["tiers"]:
        assert "vram_max_gib" in tier, f"Tier {tier['tier']} missing vram_max_gib"
        assert tier["vram_max_gib"] > 0, f"Tier {tier['tier']} has invalid vram_max_gib"


def test_ollama_candidates_cover_all_tiers(catalog):
    """Test that ollama_candidates has entries for all tiers."""
    tier_names = {t["tier"] for t in catalog["tiers"]}
    candidate_tiers = set(catalog["ollama_candidates"].keys())

    missing = tier_names - candidate_tiers
    # Allow 32gb+ to be spelled differently
    missing = {m for m in missing if not m.startswith("32")}
    assert not missing, f"Missing ollama_candidates for tiers: {missing}"


def test_driver_branches_defined(catalog):
    """Test that driver branches are defined."""
    assert "driver_branches" in catalog
    branches = catalog["driver_branches"]

    expected_branches = {"590+", "580.x", "470.x"}
    actual_branches = set(branches.keys())

    assert expected_branches == actual_branches, (
        f"Driver branches mismatch: expected {expected_branches}, got {actual_branches}"
    )


def test_model_metadata_has_required_fields(catalog):
    """Test that all model metadata entries have required fields."""
    required_fields = {"license", "distribution_ok", "parameters", "tool_support"}

    for model_id, metadata in catalog["model_metadata"].items():
        missing = required_fields - set(metadata.keys())
        assert not missing, f"Model {model_id} missing fields: {missing}"


def test_apache_licensed_models_distribution_ok(catalog):
    """Test that Apache-2.0 licensed models have distribution_ok=true."""
    for model_id, metadata in catalog["model_metadata"].items():
        if metadata.get("license") == "Apache-2.0":
            assert metadata.get("distribution_ok") is True, (
                f"Apache-2.0 model {model_id} should have distribution_ok=true"
            )


def test_llama_models_have_restrictions(catalog):
    """Test that Llama models have restriction notes."""
    for model_id, metadata in catalog["model_metadata"].items():
        if "llama" in model_id.lower():
            assert "restrictions" in metadata, (
                f"Llama model {model_id} should have restrictions field"
            )
            assert len(metadata["restrictions"]) > 0, (
                f"Llama model {model_id} should have restriction entries"
            )
