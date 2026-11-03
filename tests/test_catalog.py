import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator

from panda_federation_tools.catalog import RUN_OPTIONS, load_catalog

ROOT = Path(__file__).resolve().parents[1]
SECRET_HINTS = re.compile(r"(api_?key|token|password|secret)$", re.I)


def test_catalog_has_tools_with_unique_valid_names():
    tools = load_catalog()
    assert len(tools) >= 18
    names = [t.name for t in tools]
    assert len(names) == len(set(names))
    for name in names:
        assert re.fullmatch(r"[a-z][a-z0-9_]{0,63}", name)


def test_every_input_schema_is_valid_json_schema():
    for tool in load_catalog():
        schema = tool.input_schema
        Draft202012Validator.check_schema(schema)
        assert schema["type"] == "object"
        assert schema["additionalProperties"] is False
        assert set(schema["required"]) <= set(schema["properties"])


def test_run_options_do_not_collide_with_actor_inputs():
    for tool in load_catalog():
        assert not set(RUN_OPTIONS) & set(tool.actor_schema["properties"]), tool.name


def test_no_secret_inputs_are_exposed():
    for tool in load_catalog():
        for key in tool.actor_schema["properties"]:
            assert not SECRET_HINTS.search(key), f"{tool.name}.{key} looks like a secret"


def test_actors_and_links_point_to_owner():
    for tool in load_catalog():
        slug = tool.actor.split("/")[1]
        assert tool.actor.startswith("pandadad0214/")
        assert tool.url == f"https://apify.com/pandadad0214/{slug}"
        assert tool.name == slug.replace("-", "_")
        assert tool.pricing, f"{tool.name} has no pricing"


def test_docs_list_every_tool():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    full = (ROOT / "llms-full.txt").read_text(encoding="utf-8")
    for tool in load_catalog():
        assert f"`{tool.name}`" in readme, f"README is missing {tool.name}"
        assert tool.url in llms, f"llms.txt is missing {tool.url}"
        assert tool.url in full, f"llms-full.txt is missing {tool.url}"


def test_versions_match():
    import tomllib

    from panda_federation_tools import __version__

    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    server = json.loads((ROOT / "server.json").read_text(encoding="utf-8"))
    assert project["version"] == __version__ == server["version"]
    assert server["name"] == "io.github.pandadad0214/panda-research-mcp"


def test_readme_prices_match_the_live_catalog():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    rows = {line.split("|")[1].strip(" `"): line for line in readme.splitlines() if line.startswith("| `")}
    for tool in load_catalog():
        row = rows[tool.name]
        for price in tool.pricing:
            assert f"${price['usd']:g}" in row, f"README price for {tool.name} is out of date"


def test_readme_install_commands_use_the_current_version():
    from panda_federation_tools import __version__

    readme = "".join(
        (ROOT / f).read_text(encoding="utf-8") for f in ("README.md", "llms.txt", "llms-full.txt", "llms-install.md")
    )
    tags = set(re.findall(r"panda-federation-tools(?:\.git#|@)v(\d+\.\d+\.\d+)", readme))
    assert tags == {__version__}, tags


def test_llms_full_prices_match_the_live_catalog():
    full = (ROOT / "llms-full.txt").read_text(encoding="utf-8")
    for tool in load_catalog():
        section = full.split(f"URL: {tool.url}", 1)[1].split("\nURL: ", 1)[0]
        for price in tool.pricing:
            assert f"${price['usd']:g}" in section, f"llms-full.txt price for {tool.name} is out of date"
