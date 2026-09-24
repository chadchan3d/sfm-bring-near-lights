# v1.0.2 release provenance

## Authoritative surviving release asset

The authoritative surviving v1.0.2 release asset is:

```text
SFM_Bring_Near_Lights_v1_02.zip
````

Recorded properties:

| PropertyValue |                                                                    |
| ------------- | ------------------------------------------------------------------ |
| Size          | `29,613` bytes                                                     |
| SHA-256       | `E5940F8BC229CD325AF4AA9EE6E62B8D3CDB87EDA5A2C9087C6F9BD5329162C2` |

The original ZIP remains the release asset of record.

No claim is made that rebuilding a ZIP from the repository will reproduce the original container bytes. ZIP metadata, entry ordering, compression choices, and timestamps were not established as a reproducible build process.

## Original payload

The ZIP contains two non-directory payload files:

| PathSizeSHA-256                                         |                 |                                                                    |
| ------------------------------------------------------- | --------------- | ------------------------------------------------------------------ |
| `README.txt`                                            | `3,136` bytes   | `32ECDA40A5702AC1A93DB20DAD48EAA113E46AF481C733735141846454242BA3` |
| `workshop/scripts/sfm/animset/SFM_Bring_Near_Lights.py` | `105,382` bytes | `7F57BDF58A7273276CC1423E30B4988808276FF05940790025AB3E286D2C0051` |

The production source was reconciled to the T55-qualified source.

The ZIP’s archive paths were checked and no path traversal entry was found.

## Git baseline

Git history begins at:

```
ece86506001ed05d54cbacb14e57a4f8bf7d90f9
```

That commit is the truthful initial tracked baseline.

It contains the surviving v1.0.2 payload without inventing commits for earlier development stages.

The tracked production script and `README.txt` in that baseline match the corresponding files in the authoritative release ZIP.

The baseline must not be amended, replaced, squashed, or recreated as retrospective history.

## Publication-preparation state

The public repository may contain later ordinary commits adding:

- `README.md`;
- the complete CC0 legal text;
- a license-scope notice;
- public-safe development history;
- engineering documentation;
- release provenance;
- release validation instructions; and
- local validation tooling.

Those later files document and prepare v1.0.2 for repository publication. They do not modify the original production payload.

The eventual v1.0.2 tag may point to the final validated publication-preparation commit. It does not need to point directly to the initial import commit, provided:

- the original production payload remains byte-identical;
- the initial import remains an ancestor;
- the added files are legitimate v1.0.2 publication material; and
- provenance clearly distinguishes the original ZIP from the expanded repository state.

## Development handoff

A private development handoff was used to reconcile the project’s pre-Git chronology and supporting evidence.

Its manifest declared 23 payload files. All 23 declared hashes were independently verified.

The handoff established that:

- the exact v1.0.1 archive survived;
- T40 was the qualified ordinary-light behavior baseline;
- selected T41, T42, T48, T49, and T50 runtime evidence survived;
- selected T51–T53 intermediate sources survived;
- the T55 source matched the v1.0.2 production source; and
- the documented Light Kit progression was internally consistent.

The handoff is evidence, not fabricated Git history.

## Private evidence boundary

The following remain outside the public repository and release asset unless separately reviewed and approved:

- the complete development handoff archive;
- raw runtime logs;
- screenshots;
- intermediate development scripts;
- internal audits;
- local machine paths;
- private machine or account information; and
- other private working material.

The public repository contains sanitized conclusions rather than those private artifacts.

## Validation

Run:

```
powershell -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\validate_release.ps1 `
  -ReleaseZip '<path-to>\SFM_Bring_Near_Lights_v1_02.zip'
```

A successful result confirms:

- the original ZIP filename was supplied explicitly;
- the ZIP size matches the recorded size;
- the ZIP SHA-256 matches the authoritative digest;
- the archive contains the expected two files;
- both entry sizes and SHA-256 values match the provenance record; and
- both payload files match the corresponding files in the repository.

This validates identity and correspondence. It does not claim that the archive was reproducibly generated from the repository.
