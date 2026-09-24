# v1.0.2 release verification record

## Published state

- Repository: `chadchan3d/sfm-bring-near-lights`
- Visibility: public
- Default branch: `main`
- Initial Git baseline: `ece86506001ed05d54cbacb14e57a4f8bf7d90f9`
- v1.0.2 tag target: `fb62ce6c6736aa247e72a35a98c85b4a748902d0`
- Annotated tag: `v1.0.2`
- Tag object: `567d03f0c0bc2eeae013c823f916e2ca4db7539e`
- Release asset: `SFM_Bring_Near_Lights_v1_02.zip`
- Release asset SHA-256: `E5940F8BC229CD325AF4AA9EE6E62B8D3CDB87EDA5A2C9087C6F9BD5329162C2`

The initial baseline remains an ancestor of the published tag target. No retrospective development commits were manufactured.

Later documentation-only commits on `main` do not change the v1.0.2 tag or release payload.

## Production payload

The release payload remains:

| Path | SHA-256 |
| --- | --- |
| `README.txt` | `32ECDA40A5702AC1A93DB20DAD48EAA113E46AF481C733735141846454242BA3` |
| `workshop/scripts/sfm/animset/SFM_Bring_Near_Lights.py` | `7F57BDF58A7273276CC1423E30B4988808276FF05940790025AB3E286D2C0051` |

The production source is the final T55 source reconciled onto the v1.0.1 visual/UI base.

## Runtime evidence represented by the repository

Preserved development evidence supports the documented production mechanics, including:

- ordinary projected-light discovery and role suggestions;
- explicit selection and zero-write cancellation;
- absolute-world placement with orientation restoration;
- position, orientation, and parent verification;
- one-operation native Undo behavior in the tested cases;
- Key / Fill / Rim side flipping;
- native Light Kit recognition as one complete setup;
- whole-kit movement through `lightRoot`;
- character BODY-based whole-kit placement;
- hidden-member orientation and parent preservation; and
- fail-closed handling for unsupported relationships.

The published source was reconciled to the final T55 production source. This record does not claim a separate post-packaging runtime replay unless such a result is preserved independently.

## Documentation and license

- `README.md` describes the supported v1.0.2 behavior.
- `LICENSE` contains the complete CC0 1.0 Universal legal text.
- `LICENSE_SCOPE.md` limits the dedication to material owned and controlled by the author.
- Third-party software, names, formats, APIs, and assets are not represented as relicensed.
- `docs/DEVELOPMENT_HISTORY.md` identifies the T-series chronology as pre-Git.
- `docs/RELEASE_PROVENANCE.md` records the published tag, commit, and release asset identities.

## Privacy review

A repository review on 2026-09-24 inspected:

- both commits reachable from the published v1.0.2 history;
- current tracked text and source files;
- commit and annotated-tag metadata; and
- the two baseline payload files.

The review searched for private identity data, unrelated organizational identity, local user-profile paths, phone-like identifiers, credentials, tokens, private-key markers, and credential-like assignments.

No matches were detected within that inspected scope.

The GitHub release asset digest matches the recorded provenance. The binary release container was not independently re-opened through the repository connector during this review; its two recorded payload files are represented by the audited baseline files.

## Publication result

- The repository is public.
- `v1.0.2` identifies the intended release state.
- The v1.0.2 release asset is present with the recorded SHA-256 digest.
- No history rewrite is indicated by the current privacy findings.
- Raw development evidence remains outside the public repository.
