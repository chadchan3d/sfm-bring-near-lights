# v1.0.2 release provenance

## Published release

Repository: `chadchan3d/sfm-bring-near-lights`  
Default branch: `main`  
Release/tag: `v1.0.2`

Published v1.0.2 objects:

| Item | Value |
| --- | --- |
| Initial Git baseline | `ece86506001ed05d54cbacb14e57a4f8bf7d90f9` |
| v1.0.2 tag target | `fb62ce6c6736aa247e72a35a98c85b4a748902d0` |
| Annotated tag object | `567d03f0c0bc2eeae013c823f916e2ca4db7539e` |
| Release published | `2026-09-24T07:00:40Z` |

Git history begins with the surviving v1.0.2 payload. Earlier T-series development stages are documented as pre-Git history rather than reconstructed as commits.

Later documentation-only commits on `main` do not alter the fixed v1.0.2 tag target or release payload.

## Release asset

The published v1.0.2 asset is:

```text
SFM_Bring_Near_Lights_v1_02.zip
```

| Property | Value |
| --- | --- |
| Size | `29,613` bytes |
| SHA-256 | `E5940F8BC229CD325AF4AA9EE6E62B8D3CDB87EDA5A2C9087C6F9BD5329162C2` |

The release asset is the container of record. No claim is made that rebuilding a ZIP from the repository will reproduce identical container bytes.

## Payload

The release ZIP contains two non-directory payload files:

| Path | Size | SHA-256 |
| --- | ---: | --- |
| `README.txt` | `3,136` bytes | `32ECDA40A5702AC1A93DB20DAD48EAA113E46AF481C733735141846454242BA3` |
| `workshop/scripts/sfm/animset/SFM_Bring_Near_Lights.py` | `105,382` bytes | `7F57BDF58A7273276CC1423E30B4988808276FF05940790025AB3E286D2C0051` |

The tracked payload in the initial Git baseline matches these recorded identities. The production source was reconciled byte-for-byte to the final T55 production source.

## Publication documentation

Commit `fb62ce6c6736aa247e72a35a98c85b4a748902d0` added the public documentation, CC0 legal text and scope notice, release provenance, release verification guidance, and local validation tooling used for the v1.0.2 publication.

Those additions did not modify the original v1.0.2 production payload imported by the baseline commit.

The annotated `v1.0.2` tag points to that publication commit.

## Evidence boundary

Raw development evidence is intentionally not part of the public repository or release asset. Public documentation retains the supported conclusions, limitations, and provenance needed to understand the release without publishing internal working material.

## Validation

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\validate_release.ps1 `
  -ReleaseZip '<path-to>\SFM_Bring_Near_Lights_v1_02.zip'
```

A successful result confirms the recorded release asset identity, expected archive paths, payload sizes and SHA-256 values, and correspondence between the ZIP payload and tracked repository files.

This validates identity and correspondence. It does not claim reproducible ZIP generation.
