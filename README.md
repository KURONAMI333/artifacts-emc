# EMC for Artifacts

This data-only ProjectE addon assigns EMC to 40 Artifacts items that mainly come from exploration. Once you have found an included item, ProjectE can give it a value instead of leaving it outside the EMC map. Five toggle items have separate clean and disabled state records at the same price.

The first build targets Minecraft 1.21.1, NeoForge, Artifacts 13.2.5, and ProjectE 1.1.0. Six higher-impact items, Everlasting Beef, Eternal Steak, and the mimic spawn egg are not priced by this addon. The prices are author-designed, not pre-addon values or promises about every modpack's balance. An isolated dedicated server loaded and reloaded the final JAR with ProjectE Integration and Recipe Integration present; all 45 state identities mapped at the intended values, and all 45 preserved their component patches through ProjectE's stack reconstruction path. A player taking outputs through the client GUI and individual modpack overrides were not tested.

Build with `python3 tools/build_jar.py --values src/main/resources/data/artifacts_emc/pe_custom_conversions/artifacts_emc.json --output build/artifacts_emc-0.1.0+neoforge-1.21.1.jar`. The builder checks the 40-item allowlist and equal-value clean/disabled pairs. The released JAR contains no bundled host or ProjectE code.

The CurseForge avatar candidate is [branding/icon.png](branding/icon.png). Its [asset credits](branding/PROVENANCE.md) and [complete Artifacts MIT notice](branding/ARTIFACTS_MIT_LICENSE.txt) cover the two Artifacts textures used in that image. The icon is not embedded in the current JAR.

License: All Rights Reserved. Modpack inclusion is permitted, including monetized packs; see [LICENSE](LICENSE). Questions and bug reports: comment on the CurseForge project or DM [@kuronami333](https://x.com/kuronami333). Do not use GitHub Issues for support.
