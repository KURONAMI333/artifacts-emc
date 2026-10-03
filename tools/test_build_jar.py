from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
import tomllib

SCRIPT = Path(__file__).with_name("build_jar.py")
spec = importlib.util.spec_from_file_location("artifacts_build_jar", SCRIPT)
build_jar = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(build_jar)

class BuildJarTests(unittest.TestCase):
    def single_value(self, item_id="artifacts:whoopee_cushion", value=1):
        return {"values":{"before":[{"type":"projecte:item","id":item_id,"emc_value":value}]}}

    def test_synthetic_minimal_safe_item_packages_exact_data_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp=Path(tmp); source=tmp/"values.json"; output=tmp/"candidate.jar"
            source.write_text(json.dumps(self.single_value()),encoding="utf-8")
            self.assertEqual(build_jar.build(source,output),1)
            with zipfile.ZipFile(output) as jar:
                self.assertEqual(set(jar.namelist()),{
                    "META-INF/neoforge.mods.toml","pack.mcmeta","LICENSE_artifacts_emc",
                    "data/artifacts_emc/pe_custom_conversions/artifacts_emc.json"})
                packaged=json.loads(jar.read("data/artifacts_emc/pe_custom_conversions/artifacts_emc.json"))
                self.assertEqual(packaged,self.single_value())
                metadata=jar.read("META-INF/neoforge.mods.toml").decode()
                self.assertIn('modLoader="lowcodefml"',metadata)
                self.assertIn('modId="projecte"',metadata)
                self.assertIn('modId="artifacts"',metadata)
                pack=json.loads(jar.read("pack.mcmeta"))
                self.assertEqual(pack["pack"]["pack_format"],48)

    def test_rejects_held_unknown_empty_duplicate_and_invalid_records(self):
        bad=[
            {"values":{"before":[]}},
            self.single_value("artifacts:everlasting_beef"),
            self.single_value("artifacts:eternal_steak"),
            self.single_value("artifacts:digging_claws"),
            self.single_value("artifacts:not_real"),
            self.single_value(value=0),
            {"values":{"before":[*self.single_value()["values"]["before"]]*2}},
            {"values":{"before":[{"type":"projecte:item","id":"artifacts:whoopee_cushion","emc_value":1,"data":{"artifacts:disabled_by_toggle":{}}}]}},
        ]
        for document in bad:
            with self.subTest(document=document):
                with self.assertRaises(build_jar.BuildInputError):
                    build_jar.validate_values(document)

    def test_release_metadata_and_pack_version_are_pinned(self):
        root=Path(__file__).resolve().parents[1]
        metadata=tomllib.loads((root/"src/main/templates/META-INF/neoforge.mods.toml").read_text())
        self.assertEqual(metadata["mods"][0]["modId"],"artifacts_emc")
        deps={d["modId"]:d for d in metadata["dependencies"]["artifacts_emc"]}
        self.assertEqual(set(deps),{"minecraft","neoforge","projecte","artifacts"})
        self.assertEqual(deps["minecraft"]["versionRange"],"[1.21.1]")
        self.assertEqual(deps["projecte"]["versionRange"],"[1.1.0]")
        self.assertEqual(deps["artifacts"]["versionRange"],"[13.2.5]")
        self.assertEqual(json.loads((root/"src/main/resources/pack.mcmeta").read_text())["pack"]["pack_format"],48)

    def test_toggle_requires_both_states_with_equal_values(self):
        item="artifacts:night_vision_goggles"
        normal={"type":"projecte:item","id":item,"emc_value":8}
        disabled={**normal,"data":{"artifacts:disabled_by_toggle":{}}}
        build_jar.validate_values({"values":{"before":[normal,disabled]}})
        with self.assertRaises(build_jar.BuildInputError):
            build_jar.validate_values({"values":{"before":[normal]}})
        with self.assertRaises(build_jar.BuildInputError):
            build_jar.validate_values({"values":{"before":[normal,{**disabled,"emc_value":9}]}})

    def test_product_has_40_items_and_45_states_with_toggle_pairs(self):
        root=Path(__file__).resolve().parents[1]
        product=json.loads((root/"src/main/resources/data/artifacts_emc/pe_custom_conversions/artifacts_emc.json").read_text())
        policy=build_jar.load_policy()
        rows=product["values"]["before"]
        product_ids=[row["id"] for row in rows]
        expected=set(policy["eligible_after_individual_price_review"])
        self.assertEqual(len(rows),45)
        self.assertEqual(len(set(product_ids)),40)
        self.assertEqual(set(product_ids),expected)
        self.assertEqual(sum("data" in row for row in rows),5)
        fixture=json.loads((root/"tools/toggle_states_fixture.json").read_text())
        self.assertEqual(fixture["unit_payload_status"],"runtime_decode_verified")
        self.assertEqual(len(fixture["values"]["before"]),10)
        build_jar.validate_values({"values":fixture["values"]})

    def test_jar_build_is_reproducible(self):
        root=Path(__file__).resolve().parents[1]
        values=root/"src/main/resources/data/artifacts_emc/pe_custom_conversions/artifacts_emc.json"
        with tempfile.TemporaryDirectory() as tmp:
            first=Path(tmp)/"first.jar"; second=Path(tmp)/"second.jar"
            build_jar.build(values,first); build_jar.build(values,second)
            self.assertEqual(first.read_bytes(),second.read_bytes())

if __name__=="__main__":
    unittest.main()
