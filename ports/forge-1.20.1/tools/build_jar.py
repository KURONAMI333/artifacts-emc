#!/usr/bin/env python3
"""Build the source-only Artifacts EMC data JAR for Forge 1.20.1."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
import tomllib
import zipfile


ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "src/main/resources"
VALUES = RES / "data/artifacts_emc/pe_custom_conversions/artifacts_emc.json"
OUTPUT = ROOT / "build/artifacts_emc-0.1.0+forge-1.20.1.jar"
EXPECTED_IDS = {
    "artifacts:anglers_hat", "artifacts:antidote_vessel", "artifacts:aqua_dashers",
    "artifacts:bunny_hoppers", "artifacts:charm_of_sinking", "artifacts:chorus_totem",
    "artifacts:cloud_in_a_bottle", "artifacts:cowboy_hat", "artifacts:cross_necklace",
    "artifacts:crystal_heart", "artifacts:feral_claws", "artifacts:fire_gauntlet",
    "artifacts:flame_pendant", "artifacts:flippers", "artifacts:golden_hook",
    "artifacts:helium_flamingo", "artifacts:kitty_slippers", "artifacts:night_vision_goggles",
    "artifacts:novelty_drinking_hat", "artifacts:obsidian_skull", "artifacts:onion_ring",
    "artifacts:panic_necklace", "artifacts:plastic_drinking_hat", "artifacts:pocket_piston",
    "artifacts:power_glove", "artifacts:running_shoes", "artifacts:scarf_of_invisibility",
    "artifacts:shock_pendant", "artifacts:snorkel", "artifacts:snowshoes",
    "artifacts:steadfast_spikes", "artifacts:thorn_pendant", "artifacts:umbrella",
    "artifacts:universal_attractor", "artifacts:vampiric_glove", "artifacts:whoopee_cushion",
}
TOGGLES = {"artifacts:night_vision_goggles", "artifacts:universal_attractor"}


def validate() -> dict[str, bytes]:
    metadata_path = RES / "META-INF/mods.toml"
    metadata_text = metadata_path.read_text(encoding="utf-8")
    metadata = tomllib.loads(metadata_text)
    if metadata.get("modLoader") != "lowcodefml" or metadata.get("loaderVersion") != "[1,)":
        raise ValueError("expected Forge lowcodefml metadata")
    mods = metadata.get("mods", [])
    if len(mods) != 1 or mods[0].get("modId") != "artifacts_emc" or mods[0].get("version") != "0.1.0":
        raise ValueError("unexpected Forge addon metadata")
    deps = {item.get("modId"): item for item in metadata.get("dependencies", {}).get("artifacts_emc", [])}
    expected_deps = {"minecraft": "[1.20.1]", "forge": "[47.0.46,)", "projecte": "[1.0.1]", "artifacts": "[9.5.19]"}
    if set(deps) != set(expected_deps):
        raise ValueError("Forge target dependency set mismatch")
    for mod_id, version in expected_deps.items():
        row = deps[mod_id]
        if row.get("mandatory") is not True or row.get("versionRange") != version:
            raise ValueError(f"incorrect Forge target dependency: {mod_id}")

    pack_path = RES / "pack.mcmeta"
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    if pack.get("pack", {}).get("pack_format") != 15:
        raise ValueError("Minecraft 1.20.1 requires pack_format 15")

    values_doc = json.loads(VALUES.read_text(encoding="utf-8"))
    if set(values_doc) != {"comment", "values"} or set(values_doc["values"]) != {"before"}:
        raise ValueError("unexpected ProjectE PE1.0.1 conversion schema")
    table = values_doc["values"]["before"]
    if len(table) != 40:
        raise ValueError("expected 36 plain item IDs and four toggle-state rows")
    plain_ids = {item for item in table if "{" not in item}
    if plain_ids != EXPECTED_IDS:
        raise ValueError("plain item identities differ from the Forge 1.20.1 source scope")
    if any(type(value) is not int or value <= 0 for value in table.values()):
        raise ValueError("EMC entries must be positive integers")
    for item in TOGGLES:
        states = {item, item + "{isActivated:0b}", item + "{isActivated:1b}"}
        if not states <= table.keys() or len({table[key] for key in states}) != 1:
            raise ValueError(f"toggle state prices differ or are missing: {item}")

    logo_path = RES / "logo.png"
    license_path = ROOT / "LICENSE"
    if not logo_path.is_file() or not license_path.is_file():
        raise ValueError("canonical Forge icon or LICENSE is missing")
    entries = {
        "LICENSE_artifacts_emc": license_path.read_bytes(),
        "META-INF/mods.toml": metadata_path.read_bytes(),
        "data/artifacts_emc/pe_custom_conversions/artifacts_emc.json":
            (json.dumps(values_doc, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        "logo.png": logo_path.read_bytes(),
        "pack.mcmeta": pack_path.read_bytes(),
    }
    for name in entries:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or "\\" in name:
            raise ValueError(f"unsafe archive entry: {name}")
    return entries


def build() -> None:
    entries = validate()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as jar:
        for name, payload in sorted(entries.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.flag_bits = 0
            jar.writestr(info, payload, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(OUTPUT) as jar:
        bad = jar.testzip()
        if bad:
            raise ValueError(f"ZIP CRC failure: {bad}")
        if set(jar.namelist()) != set(entries):
            raise ValueError("JAR entry set differs from reviewed bundle")
        for name, payload in entries.items():
            if jar.read(name) != payload:
                raise ValueError(f"JAR entry differs from source: {name}")
    print(f"{OUTPUT} bytes={OUTPUT.stat().st_size}")


if __name__ == "__main__":
    build()
