"""Tests for JSON linting functionality."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest


def test_valid_json_file():
    """Test that valid JSON files are accepted."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"key": "value", "number": 42}, f)
        f.flush()
        path = Path(f.name)

    try:
        content = path.read_text()
        parsed = json.loads(content)
        assert parsed["key"] == "value"
        assert parsed["number"] == 42
    finally:
        path.unlink()


def test_invalid_json_raises():
    """Test that invalid JSON raises an error."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("{invalid json}")
        f.flush()
        path = Path(f.name)

    try:
        content = path.read_text()
        with pytest.raises(json.JSONDecodeError):
            json.loads(content)
    finally:
        path.unlink()


def test_model_catalog_valid():
    """Test that model_catalog.json is valid and has expected structure."""
    catalog_path = Path(__file__).parents[1] / "tools" / "local_llm" / "model_catalog.json"
    if not catalog_path.exists():
        pytest.skip("model_catalog.json not found")

    content = catalog_path.read_text()
    catalog = json.loads(content)

    # Check required top-level keys
    assert "tiers" in catalog
    assert "ollama_candidates" in catalog
    assert "model_metadata" in catalog

    # Check tiers structure
    assert isinstance(catalog["tiers"], list)
    assert len(catalog["tiers"]) > 0

    for tier in catalog["tiers"]:
        assert "tier" in tier
        assert "vram_max_gib" in tier

    # Check model_metadata has license info
    for model_id, metadata in catalog["model_metadata"].items():
        assert "license" in metadata, f"Model {model_id} missing license"
        assert "distribution_ok" in metadata, f"Model {model_id} missing distribution_ok"


def test_probe_models_files_valid():
    """Test that all probe_models_*.json files are valid JSON."""
    probe_dir = Path(__file__).parents[1] / "tools" / "local_llm"
    probe_files = list(probe_dir.glob("probe_models*.json"))

    assert len(probe_files) > 0, "No probe_models files found"

    for probe_file in probe_files:
        content = probe_file.read_text()
        data = json.loads(content)
        assert "models" in data, f"{probe_file.name} missing 'models' key"
        assert isinstance(data["models"], list), f"{probe_file.name} 'models' is not a list"
