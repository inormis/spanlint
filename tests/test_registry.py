from pathlib import Path

from spanlint.registry import load_registry

FIXTURES = Path(__file__).parent / "fixtures"


def test_loads_attributes_from_file() -> None:
    reg = load_registry(FIXTURES / "gen_ai.yaml")
    assert set(reg.attributes) == {
        "gen_ai.system",
        "gen_ai.request.model",
        "gen_ai.usage.input_tokens",
    }


def test_string_attribute() -> None:
    reg = load_registry(FIXTURES / "gen_ai.yaml")
    model = reg.attribute("gen_ai.request.model")
    assert model is not None
    assert model.type == "string"
    assert model.stability == "development"


def test_enum_attribute_members() -> None:
    reg = load_registry(FIXTURES / "gen_ai.yaml")
    system = reg.attribute("gen_ai.system")
    assert system is not None
    assert system.type == "enum"
    assert system.enum_members == ("openai", "anthropic")


def test_unknown_attribute_returns_none() -> None:
    reg = load_registry(FIXTURES / "gen_ai.yaml")
    assert reg.attribute("gen_ai.does_not_exist") is None


def test_loads_from_directory() -> None:
    reg = load_registry(FIXTURES)
    assert "gen_ai.system" in reg.attributes


def test_span_group_refs_are_ignored() -> None:
    reg = load_registry(FIXTURES / "gen_ai.yaml")
    assert len(reg.attributes) == 3
