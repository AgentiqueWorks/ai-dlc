"""The frontmatter parser is also the portability guard, so its refusals matter
as much as what it accepts."""

from __future__ import annotations

import pytest

from ai_dlc.yamlite import YamlLiteError, parse, split_frontmatter


def test_parses_nested_mappings_and_lists():
    data = parse(
        """
name: 01-intent-capture
allowed-tools:
  - Read
  - Bash(git commit *)
  - Agent(a, b)
metadata:
  stage: "01-plan"
  requires: ""
  maturity: stable
""".strip()
    )
    assert data["name"] == "01-intent-capture"
    assert data["allowed-tools"] == ["Read", "Bash(git commit *)", "Agent(a, b)"]
    assert data["metadata"]["stage"] == "01-plan"
    assert data["metadata"]["requires"] == ""


def test_scalars():
    data = parse("a: 1\nb: 1.5\nc: true\nd: null\ne:\nf: 'it''s'\ng: \"x\"  # comment")
    assert data == {"a": 1, "b": 1.5, "c": True, "d": None, "e": None, "f": "it's", "g": "x"}


def test_sequence_of_mappings():
    data = parse("metrics:\n  - name: a\n    tier: 1\n  - name: b\n    tier: 2")
    assert data["metrics"] == [{"name": "a", "tier": 1}, {"name": "b", "tier": 2}]


@pytest.mark.parametrize(
    "source",
    [
        "a: &anchor 1",
        "a: *alias",
        "<<: *base",
        "a: |\n  block",
        "a: >\n  folded",
        "a: [1, 2]",
        "a: {b: 1}",
        "a: 1\n\tb: 2",
    ],
)
def test_rejects_unportable_yaml(source):
    """Anything a naive third-party loader would get wrong is refused here."""
    with pytest.raises(YamlLiteError):
        parse(source)


def test_rejects_duplicate_keys():
    with pytest.raises(YamlLiteError):
        parse("a: 1\na: 2")


def test_split_frontmatter():
    front, body = split_frontmatter("---\nname: x\n---\n# Title\n")
    assert front == "name: x"
    assert body == "# Title\n"
    assert split_frontmatter("# no frontmatter")[0] is None


def test_matches_pyyaml_where_available():
    """Differential check: where PyYAML exists, we must agree with it."""
    yaml = pytest.importorskip("yaml")
    source = "name: x\nlist:\n  - a\n  - b\nmap:\n  k: 1\n  j: true\n"
    assert parse(source) == yaml.safe_load(source)
