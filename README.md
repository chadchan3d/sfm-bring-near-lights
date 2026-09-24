# SFM Bring Near: Lights

Bring Near is a Source Filmmaker Animation Set utility that moves selected existing lights into useful starting positions around a deliberately chosen model or prop.

The chosen model remains fixed. Bring Near moves only the lights the artist approves and leaves uncertain transform relationships unavailable.

Version 1.0.2 also recognizes SFM’s native Light Kit as one complete lighting setup. On supported character models, Bring Near centers the kit’s authored focus on the torso while preserving the preset arrangement.

## Installation

1. Download `SFM_Bring_Near_Lights_v1_02.zip`.
2. Extract the ZIP into:

   ```text
   SourceFilmmaker\game\
   ```

3. Restart Source Filmmaker.

The release archive contains:

```
README.txt
workshop\scripts\sfm\animset\SFM_Bring_Near_Lights.py
```

## Usage

1. In the Animation Set Editor, right-click the model or prop around which the lights should be placed.
2. Choose:
   ```
   Rig > Bring Near...
   ```
3. Select the lights to move.
4. Review or change each suggested placement.
5. Optionally enable **Flip Key / Fill / Rim sides**.
6. Choose **Bring Near**.
7. Fine-tune the resulting lighting normally.

To undo the operation, press **Ctrl+Z immediately after Bring Near finishes**.

## Placements

Bring Near recognizes common staging roles, including:

- Key
- Fill
- Backlight
- Rim
- Hair
- Floor
- Eye
- Background

Unrecognized lights can use **Nearby Only**.

Role recognition only suggests a placement. The chooser remains the artist’s approval point, and each suggestion can be changed before anything moves.

Bring Near does not create lights and does not attempt to finish the lighting setup.

## Native Light Kits

Version 1.0.2 recognizes the supported native SFM Light Kit structure as one chooser item:

**Light Kit — Whole kit centered on model**

Light Kit placement is available only when Bring Near can establish the character’s body reference; bounds-only props do not qualify for whole-kit placement.

When eligible, Bring Near translates the kit’s shared authored root to the character’s torso center while preserving the preset arrangement. It does not manipulate the hidden member lights independently.

A Light Kit remains unavailable when its expected structure or relationship safety cannot be established.

## Safety behavior

Before writing, Bring Near:

- resolves the current shot;
- validates the deliberately invoked anchor;
- inventories projected lights and supported native Light Kits in the shot;
- maps movable targets to their exact animation sets and transform controls;
- applies bounded parent and relationship checks;
- builds the complete movement plan;
- revalidates the document, shot, anchor, and target identities after the chooser closes; and
- verifies position, orientation, and parent identity after movement.

Lights involved in unsupported parent, lock, or other transform relationships are unavailable rather than moved speculatively.

The tool fails closed when required identity, transform, reference, or relationship information is uncertain.

## Product scope

Bring Near is intentionally narrow:

- current shot only;
- existing projected lights, plus the supported native SFM Light Kit;
- model or prop remains the fixed anchor;
- ordinary lights move independently; the supported Light Kit moves as one complete setup;
- no camera workflow;
- no Master or Normalizer dependency;
- no offline model database or scanner dependency;
- no general-purpose transform framework;
- no deep animation-channel, log, layer, or key traversal; and
- no synthetic reverse-move Undo system.

The primary workflow is initial light staging in short, often still-shot clips.

## Compatibility

Bring Near targets Source Filmmaker’s bundled Python 2.7.5 environment, PySide, and SFM Python bindings.

## Repository contents

- `workshop/scripts/sfm/animset/SFM_Bring_Near_Lights.py` — production script.
- `README.txt` — installation and usage text shipped in the original v1.0.2 ZIP.
- `LICENSE` — complete CC0 1.0 Universal legal text.
- `LICENSE_SCOPE.md` — scope of the CC0 dedication and third-party exclusions.
- `docs/DEVELOPMENT_HISTORY.md` — public-safe pre-Git development chronology.
- `docs/ENGINEERING_NOTES.md` — architecture and implementation contract.
- `docs/RELEASE_PROVENANCE.md` — published release identity and provenance.
- `docs/RELEASE_CHECKLIST.md` — v1.0.2 release verification record.
- `tools/validate_release.ps1` — validates the original release ZIP against the tracked payload.

## Development history

The project predates this Git repository.

The first truthful Git commit is:

```
ece86506001ed05d54cbacb14e57a4f8bf7d90f9
```

Earlier T-series stages are preserved as a documented pre-Git chronology. They are not represented as historical Git commits.

See [`docs/DEVELOPMENT_HISTORY.md`](docs/DEVELOPMENT_HISTORY.md).

## Release provenance

The authoritative v1.0.2 release asset is:

```
SFM_Bring_Near_Lights_v1_02.zip
```

Its recorded SHA-256 is:

```
E5940F8BC229CD325AF4AA9EE6E62B8D3CDB87EDA5A2C9087C6F9BD5329162C2
```

See [`docs/RELEASE_PROVENANCE.md`](docs/RELEASE_PROVENANCE.md) for the complete payload record.

## Author

ChadChan3D
[https://ChadChan3D.com/assets/](https://chadchan3d.com/assets/)

## License

Material owned by ChadChan3D and within the author’s authority to dedicate is released under CC0 1.0 Universal.

See [`LICENSE`](LICENSE) and [`LICENSE_SCOPE.md`](LICENSE_SCOPE.md).

Source Filmmaker and other third-party names, software, formats, APIs, and assets remain the property of their respective owners. They are not included in or relicensed by this repository.
