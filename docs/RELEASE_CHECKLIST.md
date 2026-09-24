# v1.0.2 release checklist

## Repository state

- [ ] The initial Git baseline remains unchanged:

  ```text
  ece86506001ed05d54cbacb14e57a4f8bf7d90f9
````

- The baseline is an ancestor of the proposed v1.0.2 tag target.
- No retrospective development commits were manufactured.
- The working tree is clean.
- `git fsck --full` completes successfully.
- The intended public branch and tag are the only refs selected for publication.
- No remote or publication action occurs before separate publication approval.

## Production payload

- `README.txt` remains unchanged from the authoritative ZIP.
- `workshop/scripts/sfm/animset/SFM_Bring_Near_Lights.py` remains unchanged from the authoritative ZIP.
- Production source SHA-256 is:
  ```
  7F57BDF58A7273276CC1423E30B4988808276FF05940790025AB3E286D2C0051
  ```
- Release README SHA-256 is:
  ```
  32ECDA40A5702AC1A93DB20DAD48EAA113E46AF481C733735141846454242BA3
  ```

## Original release asset

- Filename is:
  ```
  SFM_Bring_Near_Lights_v1_02.zip
  ```
- Size is:
  ```
  29,613 bytes
  ```
- SHA-256 is:
  ```
  E5940F8BC229CD325AF4AA9EE6E62B8D3CDB87EDA5A2C9087C6F9BD5329162C2
  ```
- `tools/validate_release.ps1` reports PASS.
- No claim of byte-reproducible ZIP generation is made.

## Python validation

- The exact production source compiles with Python 2.7.5.
- Compilation is performed from a temporary copy so no `.pyc` file enters the repository.
- Generic Python compilation is described only as syntax/bytecode validation.
- Python compilation is not represented as proof of SFM runtime behavior.

## SFM runtime validation

The historical evidence qualifies the production mechanics documented in this repository.

If a final installation smoke test is performed, use the exact packaged script and record the result privately.

- Right-clicking a model or prop exposes **Rig > Bring Near...**.
- The chooser identifies the deliberately invoked model.
- Ordinary projected lights appear with expected role suggestions.
- Cancel closes the chooser with zero writes.
- An approved ordinary light moves to the selected placement.
- The ordinary light’s orientation is preserved.
- The ordinary light’s parent identity is preserved.
- One immediate Ctrl+Z restores the ordinary-light operation.
- Flip changes only Key, Fill, and Rim lateral sides.
- A supported native Light Kit appears as one `Light Kit` row.
- Hidden Light Kit members do not appear as separate ordinary rows.
- Moving the Light Kit translates the complete setup through `lightRoot`.
- The Light Kit is centered using a qualified BODY reference.
- Hidden member orientations and parent identities remain preserved.
- An independent ordinary light remains separately selectable.
- Unsupported relationship cases are unavailable rather than moved.
- No raw machine-local test log is added to the public repository.

## Documentation and license

- `README.md` matches the supported v1.0.2 contract.
- `LICENSE` contains the complete CC0 1.0 Universal legal text.
- `LICENSE_SCOPE.md` limits the dedication to material owned and controlled by the author.
- Third-party software, names, formats, APIs, and assets are not represented as relicensed.
- `docs/DEVELOPMENT_HISTORY.md` clearly labels the T-series chronology as pre-Git.
- `docs/RELEASE_PROVENANCE.md` distinguishes the ZIP, Git baseline, later documentation, and private evidence.
- Documentation does not claim a reproducible ZIP build.
- Documentation does not claim that excluded raw evidence is public.

## Privacy and publication audit

- Every Git object reachable from the proposed public branch and tag has been scanned.
- Author, committer, and proposed tagger metadata use the approved public identity.
- Commit messages and tag messages have been scanned.
- Current tracked files have been scanned.
- The original release ZIP and its internal entries have been scanned.
- No raw logs, screenshots, intermediate scripts, internal audits, or private handoff archive are tracked.
- No private local path or private machine/account identifier is present.
- No unrelated work or nonprofit identity is present.
- No credential, token, private key, cookie, webhook secret, or authentication file is present.
- Scan results are reported as bounded findings, not as a guarantee that no secret could exist.

## Knowledge transfer

- The knowledge package is staged outside the project repository.
- Only sanitized prose and deliberately selected public-safe evidence are included.
- Raw logs and screenshots are excluded.
- Candidate and evidence identifiers are unique and stable.
- Private evidence is represented only as `private-evidence-exists`.
- The package contains no absolute local path.
- The package has been independently privacy-scanned.
- The package source commit is updated to the final audited publication-preparation commit.
- Publication state remains `pending` until external publication is verified.

## Tag preparation

- The complete commit sequence since the immutable baseline has been reviewed.
- The proposed v1.0.2 tag target is the final validated publication-preparation commit.
- The proposed tag target still contains the exact original production payload.
- The annotated tag would use the approved public identity.
- The tag has not been created before the tag-target review.
- The tag has not been pushed.

## External publication

- A separate publication manifest has been prepared.
- Destination owner, repository name, visibility, description, refs, tag target, and release asset are explicit.
- Authentication and destination existence have been checked without exposing credentials.
- Publication approval has been granted for the exact manifest.
- No repository creation, push, tag upload, release creation, asset upload, visibility change, or deployment occurs before that approval.
