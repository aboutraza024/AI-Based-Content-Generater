import pytest
from app.utils.humanization_linter import linter

def test_semicolon_removal():
    text = "Content marketing is essential; it drives long-term customer engagement."
    cleaned, report = linter.clean(text)
    assert ";" not in cleaned
    assert "Content marketing is essential. It drives" in cleaned
    assert report.semicolons_removed == 1

def test_oxford_comma_removal():
    text = "We offer speed, reliability, and security for all clients, or users."
    cleaned, report = linter.clean(text)
    assert ", and" not in cleaned
    assert ", or" not in cleaned
    assert "speed, reliability and security" in cleaned
    assert report.oxford_commas_removed == 2

def test_em_dash_replacement():
    text = "Our software—built with cutting-edge tech—delivers instant results."
    cleaned, report = linter.clean(text)
    assert "—" not in cleaned
    assert report.hyphens_removed >= 1

def test_consecutive_sentence_starts():
    text = "This tool is fast. This tool saves money. This tool improves workflow."
    cleaned, report = linter.clean(text)
    assert report.repetitive_starts_fixed >= 1
    # Check that third sentence start was altered
    assert "Additionally" in cleaned or "In fact" in cleaned

def test_ai_buzzwords_replacement():
    text = "We delve into utilizing synergy furthermore to create robust solutions."
    cleaned, report = linter.clean(text)
    assert "delve into" not in cleaned
    assert "explore" in cleaned or "look into" in cleaned
    assert "utilizing" not in cleaned
