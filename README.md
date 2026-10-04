# EMC for Artifacts

This data-only ProjectE addon assigns EMC to 40 Artifacts items that mainly come from exploration. Once you have found an included item, ProjectE can give it a value instead of leaving it outside the EMC map. Five toggle items have separate clean and disabled state records at the same price.

The first build targets Minecraft 1.21.1, NeoForge, Artifacts 13.2.5, and ProjectE 1.1.0. Six higher-impact items, Everlasting Beef, Eternal Steak, and the mimic spawn egg are not priced by this addon. The prices are author-designed, not pre-addon values or promises about every modpack's balance. An isolated dedicated server loaded and reloaded the final JAR with ProjectE Integration and Recipe Integration present; all 45 state identities mapped at the intended values, and all 45 preserved their component patches through ProjectE's stack reconstruction path. A player taking outputs through the client GUI and individual modpack overrides were not tested.

Build with `python3 tools/build_jar.py --values src/main/resources/data/artifacts_emc/pe_custom_conversions/artifacts_emc.json --output build/artifacts_emc-0.1.0+neoforge-1.21.1.jar`. The builder checks the 40-item allowlist and equal-value clean/disabled pairs. The released JAR contains no bundled host or ProjectE code.

## Forge 1.20.1 port

The Forge port targets Minecraft 1.20.1, Forge 47.0.46+, Artifacts 9.5.19, and ProjectE PE1.0.1. Build its JAR with Python 3.11+ using `python3 ports/forge-1.20.1/tools/build_jar.py`; the output is `ports/forge-1.20.1/build/emc-for-artifacts-0.1.0+forge-1.20.1.jar`. The portable source, icon, and `LICENSE` are under `ports/forge-1.20.1/`.

The Forge conversion table covers 36 ordinary tagged items plus four toggle-state identities (40 records total). Its runtime evidence is limited: representative price checks recorded 8192 EMC for both Night Vision Goggles and Universal Attractor in their default, OFF, and ON states. R7 then verified normal save/reopen and persistence of the toggled OFF state in the head and belt slots, followed by a clean client exit. The exact Forge JAR is 9008 bytes, SHA-256 `97dd67449800ff630267f2c7ef15dda146c3548fe6f6193c8056ab66c5e9aaaa`. All 40 identities were not individually inspected as live tooltips, and ProjectE transmutation/condenser output was not asserted.

The CurseForge avatar candidate is [branding/icon.png](branding/icon.png). Its [asset credits](branding/PROVENANCE.md) and [complete Artifacts MIT notice](branding/ARTIFACTS_MIT_LICENSE.txt) cover the two Artifacts textures used in that image. The icon is not embedded in the current JAR.

License: All Rights Reserved. Modpack inclusion is permitted, including monetized packs; see [LICENSE](LICENSE). Questions and bug reports: comment on the CurseForge project or DM [@kuronami333](https://x.com/kuronami333). Do not use GitHub Issues for support.
