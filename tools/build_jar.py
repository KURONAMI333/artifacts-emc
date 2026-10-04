#!/usr/bin/env python3
"""Package the code-free lowcodefml Artifacts EMC addon after prices are approved.

This packager intentionally contains no price table. It accepts a reviewed ProjectE
1.21.1 values document as input and refuses held, unknown, partial-state, or invalid IDs.
"""
from __future__ import annotations
import argparse
import json
import tomllib
from pathlib import Path, PurePosixPath
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MOD_ID = "artifacts_emc"
POLICY_PATH = ROOT / "tools/item_policy.json"
TOGGLE_PATCH_KEY = "artifacts:disabled_by_toggle"


class BuildInputError(ValueError):
    pass

def load_policy() -> dict:
    policy=json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    tag=set(policy["artifact_tag_ids"])
    eligible=set(policy["eligible_after_individual_price_review"])
    held_rows=policy["held_for_price_review"]+policy["held_recipe_output"]+policy["excluded_outside_tag"]
    held=set(held_rows)
    toggles=set(policy["toggle_ids"])
    if (len(tag)!=len(policy["artifact_tag_ids"]) or len(eligible)!=len(policy["eligible_after_individual_price_review"])
            or len(held)!=len(held_rows) or len(toggles)!=len(policy["toggle_ids"])):
        raise BuildInputError("duplicate ID in item policy")
    if eligible & held or toggles-eligible or len(toggles)!=len(policy["toggle_ids"]):
        raise BuildInputError("inconsistent item policy scopes")
    if eligible | (held & tag) != tag:
        raise BuildInputError("item policy does not reconcile the official Artifacts item tag")
    return policy

def validate_values(raw: object) -> dict:
    policy=load_policy()
    all_tag_ids=set(policy["artifact_tag_ids"])
    eligible=set(policy["eligible_after_individual_price_review"])
    held_ids=set(policy["held_for_price_review"]) | set(policy["held_recipe_output"]) | set(policy["excluded_outside_tag"])
    toggle_ids=set(policy["toggle_ids"])
    if not isinstance(raw, dict) or set(raw) != {"values"}:
        raise BuildInputError("input must contain only the ProjectE values object")
    values = raw["values"]
    if not isinstance(values, dict) or set(values) != {"before"} or not isinstance(values["before"], list):
        raise BuildInputError('expected {"values":{"before":[...]}}')
    rows = values["before"]
    if not rows:
        raise BuildInputError("empty values list: no EMC addon would be produced")
    state_by_id: dict[str, set[str]] = {}
    value_by_id: dict[str, dict[str, int]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise BuildInputError("every values.before entry must be an object")
        if not set(row) <= {"type", "id", "emc_value", "data"}:
            raise BuildInputError("unsupported keys in values.before entry")
        if row.get("type") != "projecte:item":
            raise BuildInputError("every entry must use type=projecte:item")
        item_id = row.get("id")
        if item_id not in all_tag_ids:
            raise BuildInputError(f"unknown/non-tag Artifacts ID: {item_id!r}")
        if item_id in held_ids:
            raise BuildInputError(f"held or excluded ID is not accepted: {item_id}")
        if item_id not in eligible:
            raise BuildInputError(f"ID is not eligible for this reviewed scope: {item_id}")
        value = row.get("emc_value")
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise BuildInputError(f"emc_value must be a positive integer: {item_id}")
        data = row.get("data")
        if "data" not in row:
            state = "normal"
        elif data == {TOGGLE_PATCH_KEY: {}}:
            state = "disabled"
        else:
            raise BuildInputError(f"unrecognized or unverified stack data: {item_id}")
        if item_id not in toggle_ids and state != "normal":
            raise BuildInputError(f"data-bearing state is only allowed for toggle items: {item_id}")
        states = state_by_id.setdefault(item_id, set())
        values = value_by_id.setdefault(item_id, {})
        if state in states:
            raise BuildInputError(f"duplicate item/state record: {item_id} ({state})")
        states.add(state)
        values[state] = value
    # Avoid publishing a toggle item that loses EMC when its state changes.
    for item_id, states in state_by_id.items():
        if item_id in toggle_ids:
            if states != {"normal", "disabled"}:
                raise BuildInputError(f"toggle item must define both normal and disabled identities: {item_id}")
            if value_by_id[item_id]["normal"] != value_by_id[item_id]["disabled"]:
                raise BuildInputError(f"toggle states must have equal EMC: {item_id}")
    return raw

def safe_archive_path(name: str) -> str:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "\\" in name:
        raise BuildInputError(f"unsafe archive path: {name}")
    return path.as_posix()

def build(values_path: Path, output_path: Path) -> int:
    raw = json.loads(values_path.read_text(encoding="utf-8"))
    validate_values(raw)
    metadata = ROOT / "src/main/templates/META-INF/neoforge.mods.toml"
    meta_doc = tomllib.loads(metadata.read_text(encoding="utf-8"))
    if meta_doc["mods"][0]["modId"] != MOD_ID or meta_doc["mods"][0]["displayName"] != "EMC for Artifacts":
        raise BuildInputError("final series identity mismatch")
    pack_meta = ROOT / "src/main/resources/pack.mcmeta"
    for required in (metadata, pack_meta):
        if not required.is_file():
            raise BuildInputError(f"required resource missing: {required.relative_to(ROOT)}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    emc_path = safe_archive_path(f"data/{MOD_ID}/pe_custom_conversions/{MOD_ID}.json")
    entries = {
        "META-INF/neoforge.mods.toml": metadata.read_bytes(),
        "pack.mcmeta": pack_meta.read_bytes(),
        "LICENSE_artifacts_emc": (ROOT / "LICENSE").read_bytes(),
        emc_path: (json.dumps(raw, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
    }
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as jar:
        for name, payload in sorted(entries.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.flag_bits = 0
            jar.writestr(info, payload, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    return len(raw["values"]["before"])

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--values", type=Path, required=True, help="reviewed price values JSON; no defaults are bundled")
    parser.add_argument("--output", type=Path, required=True, help="output JAR path")
    args = parser.parse_args()
    try:
        count = build(args.values, args.output)
    except (BuildInputError, OSError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        parser.error(str(exc))
    print(f"Packaged {count} reviewed EMC state records to {args.output}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
