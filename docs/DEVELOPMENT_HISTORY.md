# Development history

SFM Bring Near: Lights was developed and released before this Git repository existed.

This document preserves a public-safe chronology supported by surviving project source, test records, runtime evidence, audits, and release artifacts.

The T-series stages described below:

- predate Git tracking;
- are development and test identifiers;
- are not historical Git commits; and
- must not be interpreted as a reconstructed commit history.

Git history begins truthfully at:

```text
ece86506001ed05d54cbacb14e57a4f8bf7d90f9
````

That commit imports the surviving v1.0.2 release payload. No retrospective commits were manufactured for earlier stages.

## Product direction

The project converged on a narrow product contract:

- the artist deliberately invokes Bring Near from a model or prop animation set;
- that invoked model is the fixed anchor;
- Bring Near discovers projected lights in the current shot;
- the artist approves which eligible lights move;
- ordinary staging lights receive rough character-relative placements;
- uncertain, persistent, environmental, parented, locked, or otherwise ambiguous lights fail closed;
- lights move and the model does not;
- the tool is primarily a lighting workflow utility;
- cameras are outside the V1 contract;
- Master and Normalizer are not dependencies;
- the production script has no offline scanner or model-corpus dependency; and
- native SFM Undo is used instead of a synthetic reverse-move system.

## Foundation established before the final release series

Earlier live testing established the implementation foundations later retained by the release candidate:

- Rig/ANIMSET invocation identified the deliberately selected anchor.
- The anchor’s evaluated absolute-world transform could be read.
- A spawned projected light could be mapped through its cast DAG to the exact transform control used for writing.
- `sfm.Move(..., space="World")` behaved as an absolute-world position writer in the tested context.
- `sfm.Move` could disturb orientation, requiring explicit orientation restoration.
- Capturing evaluated world orientation, performing the absolute-world move, and then restoring orientation with `sfm.Rotate` produced the repaired writer.
- The tested SFM rotation component mapping was:
  ```
  Rotate(X, Y, Z) = (roll, pitch, yaw)
  ```
- The repaired writer preserved sampled later position animation in the tested fixture when writing at frame 0.
- One immediate native Ctrl+Z recovered tested successful and partial writes.
- Full-batch preflight rejection produced zero writes.
- Failures after mutation could leave partial state, making immediate native Undo part of the failure contract.
- Deep channel, log, layer, and key introspection caused a native SFM crash and was quarantined.
- Semantic role recognition remained advisory; explicit user selection remained the movement authority.

## T36 — whole-script release audit

T36 was an independent whole-script release audit of the ordinary-light production candidate.

The audit found no release-blocking architecture defect. It identified three bounded UI or robustness corrections that could be applied without reopening placement geometry or mutation mechanics.

The durable conclusion was that the core architecture was proportionate for the product:

1. resolve the invoked anchor and current shot;
2. build a bounded current-shot light inventory;
3. qualify source and relationship safety;
4. derive conservative character-relative references;
5. present explicit choices;
6. revalidate context after the chooser;
7. plan the complete batch before writing;
8. write through one native recording operation;
9. verify final state; and
10. rely on one immediate native Ctrl+Z if a post-write failure occurs.

## T40 — qualified ordinary-light release behavior

T40 incorporated the accepted T36 corrections and the final user-facing Flip behavior.

The authoritative T40 ledger records PASS.

The focused live qualification covered:

- successful chooser invocation;
- clean cancellation with zero writes;
- BODY-based placement;
- exact `eyes` attachment use;
- strict paired-eye and head fallback behavior;
- Clip Editor and Motion Editor invocation;
- blocked relationship presentation;
- selected-target position verification;
- selected-target orientation verification;
- parent preservation;
- post-chooser context stability;
- Key, Fill, and Rim lateral-side flipping; and
- preservation of placement behavior outside the explicitly flipped roles.

The T40 planner changed only the model-relative lateral offset for Key, Fill, and Rim when Flip was enabled. It did not change role assignment, forward or vertical offsets, aim targets, duplicate staggering, or other placement types.

T40 became the qualified behavior baseline for ordinary lights.

## v1.0.0

The first public version established the core Bring Near workflow for existing lights.

No retrospective Git commit has been created for this release.

## v1.0.1

Version 1.0.1 added UI polish and spacing improvements.

A surviving v1.0.1 archive provided the visual and UI base from which the final Light Kit-compatible source was rebuilt. The archive itself is not part of this public repository.

## Light Kit discovery

SFM’s native Session Presets expose one visible `lightKit` controller in the Animation Set Editor.

The same shot data contains four hidden projected-light animation sets corresponding to Key, Fill, Rim, and Bounce. These members are arranged beneath a shared transform root.

The original ordinary-light inventory could see the hidden projected lights and initially treated them as independent candidates. Runtime testing showed that this was unsafe and mechanically incorrect for the native kit.

## T41 — hidden-member write failure

T41 isolated the failure on an individual hidden Light Kit member.

Observed behavior:

- the hidden Key light was discovered;
- it passed the ordinary projected-light identity checks;
- absolute-world translation succeeded;
- the following orientation write did not take effect; and
- final verification failed with approximately 165 degrees of orientation error.

The result falsified the assumption that a hidden native Light Kit member could be handled as an ordinary independent light.

The project stopped pursuing independent hidden-member movement.

## T42 — channel-state diagnosis

T42 examined the failed hidden-member path without adopting unsafe deep traversal.

Observed behavior:

- position and orientation controls and logs were structurally present;
- both entered the expected recording context;
- the move changed relevant channel state; and
- the subsequent rotation still did not author the hidden member’s orientation successfully.

This supported a design revision rather than another special-case rotation workaround.

The hidden members would be treated as parts of one native setup.

## T43–T47 — bounded Light Kit investigation

The surviving public-safe evidence does not support separate durable conclusions for every intermediate identifier in this range.

These stages formed the bounded investigation between the failed independent-member path and the qualified common-root experiments.

They are retained here as part of the real stage numbering, but no detailed result is invented where the preserved evidence does not establish one.

## T48 — common-root movement

T48 identified the native Light Kit transform as `lightRoot` and tested movement of that root.

Observed behavior:

- all four hidden projected lights were parented beneath the same root;
- moving `lightRoot` by +384 world units on X moved every hidden member by the same delta;
- measured member orientation drift was zero; and
- member parent identities were preserved.

Result: PASS.

This established shared-root translation as the viable Light Kit movement mechanism.

## T49 — authored focus geometry

T49 was a zero-write geometry test.

The hidden members’ evaluated aim rays converged essentially on `lightRoot`. Principal-member and all-member solutions agreed within the measured tolerances.

This supported the inference that `lightRoot` represents the Light Kit’s authored subject or focus point.

The test did not mutate the scene.

## T50 — character-relative Light Kit placement

T50 moved `lightRoot` to the invoked character’s qualified BODY torso center.

Observed behavior:

- the root reached the requested destination within approximately one millionth of a world unit;
- all four hidden members followed;
- member delta errors remained negligible;
- member orientations were preserved within the tested tolerances; and
- member parent identities remained unchanged.

Result: PASS.

This established the V1 placement rule: center the complete native Light Kit on the chosen character by translating its authored focus root.

## T51 — initial production integration

T51 integrated native Light Kit recognition into the chooser.

The four hidden members were collapsed into one visible row named `Light Kit`.

The first integration produced a false-positive safety rejection. Ordinary-light child rules had been applied to the kit root even though that root’s purpose is to carry its internal lights.


## T52 — separate root-safety semantics

T52 separated Light Kit root qualification from ordinary-light qualification.

The revised rule allowed the expected hidden members beneath the kit root while retaining conservative checks for unrelated relationships.

Runtime feedback indicated that:

- the Light Kit integration worked;
- the kit appeared as one chooser row; and
- independent ordinary lights in the same shot remained available as ordinary rows.


## T53 — safety hardening and release presentation

T53 added two important release safeguards:

1. Light Kit movement requires a qualified character BODY frame. A generic BOUNDS or ROOT-only fallback is insufficient for whole-kit placement.
2. Whole-kit movement is blocked when an unrelated user-visible scene animation-set DAG is detected beneath `lightRoot`, preventing collateral movement.

T53 also incorporated the supplied Bring Near icon and final author/license presentation.

## T54 — discarded visual regression

T54 contained the intended Light Kit mechanics but was based on an older visual source.

Its UI and font presentation regressed relative to the released v1.0.1 interface.

T54 was rejected as a production source baseline.

No part of its visual regression should be revived merely because its stage number is later.

## T55 — final v1.0.2 production source

T55 rebuilt the Light Kit work on the exact surviving v1.0.1 visual and UI base.

It retained:

- the ordinary-light behavior qualified through T40;
- shared-root Light Kit movement;
- BODY-only Light Kit placement eligibility;
- unrelated-dependent safety blocking;
- the supplied application icon;
- final author and CC0 presentation; and
- the released chooser wording.


The authoritative v1.0.2 ZIP contains production source reconciled byte-for-byte to T55 and published as the v1.0.2 release payload.

The source SHA-256 is:

```
7F57BDF58A7273276CC1423E30B4988808276FF05940790025AB3E286D2C0051
```

## Git baseline

The new repository begins with one truthful baseline commit:

```
ece86506001ed05d54cbacb14e57a4f8bf7d90f9
```

That commit imports the surviving v1.0.2 payload without pretending that earlier T-series stages were commits.

Publication documentation, the complete CC0 legal text, validation tooling, and public-safe engineering notes belong in later ordinary preparation commits.

## Evidence boundary

Raw development evidence is intentionally excluded from the public repository. This document retains the supported conclusions and known limitations needed to understand the pre-Git chronology without publishing internal working material.
