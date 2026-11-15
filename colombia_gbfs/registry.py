"""Limit PyBikes discovery to Colombia and register local adapters.

Hyper uses both pybikes.data._traverse_lib and pybikes.get(). We must update
both discovery paths before importing citybikes.hyper.publisher. This adapter
lives outside the upstream PyBikes distribution, so upstream remains updatable.
"""
import importlib
import json
import os
import re
import sys
from pathlib import Path

DEFAULT_NETWORKS = "encicla,tembici-bogota"
DEFAULT_REGISTRY = "/app/config/scrapers.json"
TAG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
MODULE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
CLASS_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def enabled_networks(value=None):
    raw = os.getenv("ENABLED_NETWORKS", DEFAULT_NETWORKS) if value is None else value
    result = [tag.strip() for tag in raw.split(",")]
    if not result or any(not TAG_PATTERN.fullmatch(tag) for tag in result):
        raise ValueError("ENABLED_NETWORKS must be a comma-separated list of network tags")
    if len(result) != len(set(result)):
        raise ValueError("ENABLED_NETWORKS contains duplicate tags")
    return result


def load_registry(path=None):
    location = Path(path or os.getenv("SCRAPER_REGISTRY", DEFAULT_REGISTRY))
    entries = json.loads(location.read_text(encoding="utf-8"))
    if not isinstance(entries, list):
        raise ValueError("Scraper registry must contain a JSON array")

    tags = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Each scraper entry must be an object")
        tag = entry.get("tag")
        slug = entry.get("module")
        class_name = entry.get("class")
        meta = entry.get("meta")
        if not isinstance(tag, str) or not TAG_PATTERN.fullmatch(tag):
            raise ValueError(f"Invalid custom scraper tag: {tag!r}")
        if not isinstance(slug, str) or not MODULE_PATTERN.fullmatch(slug):
            raise ValueError(f"Invalid scraper module for {tag}")
        if not isinstance(class_name, str) or not CLASS_PATTERN.fullmatch(class_name):
            raise ValueError(f"Invalid scraper class for {tag}")
        if not isinstance(meta, dict) or meta.get("country") != "CO":
            raise ValueError(f"Scraper {tag} must declare meta.country=CO")
        if not all(meta.get(key) is not None for key in ("name", "city", "latitude", "longitude")):
            raise ValueError(f"Scraper {tag} lacks required network metadata")
        if tag in tags:
            raise ValueError(f"Duplicate custom scraper: {tag}")
        tags.add(tag)
    return entries


def activate(allowed=None, registry_path=None):
    """Register exactly the selected CO networks with PyBikes/Hyper.

    This must run before importing citybikes.hyper.publisher.
    """
    import pybikes.data as data
    from pybikes.base import BikeShareSystem

    names = enabled_networks() if allowed is None else list(allowed)
    if not names or any(not TAG_PATTERN.fullmatch(tag) for tag in names):
        raise ValueError("At least one valid network tag is required")
    if len(names) != len(set(names)):
        raise ValueError("Duplicate enabled network tags")

    # Save original discovery so repeated calls (and tests) are deterministic.
    if not hasattr(data, "_colombia_upstream_traverse"):
        data._colombia_upstream_traverse = data._traverse_lib
    upstream_entries = list(data._colombia_upstream_traverse())
    upstream_by_tag = {entry["tag"]: (module, cls, entry)
                       for module, cls, entry in upstream_entries}
    registry = load_registry(registry_path)
    custom_by_tag = {entry["tag"]: entry for entry in registry}
    selected = []
    aliases = {}

    for tag in names:
        if tag in upstream_by_tag:
            module, cls, entry = upstream_by_tag[tag]
            if entry.get("meta", {}).get("country") != "CO":
                raise ValueError(f"Refusing non-Colombian upstream network: {tag}")
            selected.append((module, cls, entry))
            continue
        spec = custom_by_tag.get(tag)
        if spec is None:
            raise ValueError(f"Unknown Colombian network: {tag}")
        module_name = "colombia_" + spec["module"]
        module = importlib.import_module("colombia_gbfs.scrapers." + spec["module"])
        cls = getattr(module, spec["class"])
        if not isinstance(cls, type) or not issubclass(cls, BikeShareSystem):
            raise TypeError(f"{tag}: adapter must subclass BikeShareSystem")
        if module_name in aliases and aliases[module_name] is not module:
            raise ValueError(f"Duplicate adapter module: {module_name}")
        aliases[module_name] = module
        selected.append((module_name, spec["class"],
                         {"tag": spec["tag"], "meta": spec["meta"]}))

    for alias, module in aliases.items():
        sys.modules["pybikes." + alias] = module

    def only_colombia():
        yield from selected

    data._traverse_lib = only_colombia
    data._traversor = only_colombia()
    data._t_cache.clear()
    return selected
