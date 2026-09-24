# Engineering notes

These notes describe the SFM Bring Near: Lights v1.0.2 architecture and the runtime evidence that supports it.

They do not define a general-purpose Source Filmmaker transform or animation framework.

## Product contract

Bring Near is invoked from the Animation Set Editor through a deliberately chosen model or prop animation set.

That animation set is the fixed anchor.

The tool:

1. resolves the current document and shot;
2. validates the invoked anchor;
3. discovers projected lights and the supported native Light Kit in the current shot;
4. maps each light to its exact animation set and transform control;
5. applies conservative relationship and placement eligibility rules;
6. presents the eligible choices;
7. revalidates context after the chooser closes;
8. builds the complete movement plan before mutation;
9. writes the approved plan through SFM’s native recording path; and
10. verifies the resulting transforms and parent identities.

The character or prop does not move.

## Evidence classifications

This document uses three practical categories:

- **Observed:** directly established by preserved live SFM runtime evidence.
- **Production rule:** behavior implemented by the v1.0.2 source in response to that evidence.
- **Limitation:** behavior that remains outside the supported V1 contract or was not proven generally.

## Anchor and target identity

**Observed:** Rig/ANIMSET invocation identifies the animation set on which the artist deliberately invoked Bring Near.

**Observed:** The anchor’s evaluated absolute-world transform can be read in the tested SFM context.

**Observed:** A projected-light operator can be traced through its cast DAG to the exact animation set and transform control used for movement.

**Production rule:** Identity is established from live objects in the current shot. Generic global name guessing is not used as a substitute.

**Production rule:** The document, shot, anchor, target animation sets, transform controls, and relevant parent identities are revalidated after the modal chooser closes.

**Production rule:** A mismatch or ambiguous identity fails closed before movement.

## Ordinary-light writer

**Observed:** In the tested SFM context:

```python
sfm.Move(..., space="World")
```

writes the supplied position as an absolute-world destination.

It is not a relative world-space delta operation.

**Observed:** `sfm.Move` can disturb a light’s evaluated orientation.

**Observed:** The repaired sequence is:

1. capture the evaluated world orientation;
2. call `sfm.Move` with the absolute-world destination;
3. restore the saved orientation using `sfm.Rotate`; and
4. verify the final position, orientation, and parent identity.

The tested SFM rotation component mapping is:

```
Rotate(X, Y, Z) = (roll, pitch, yaw)
```

**Production rule:** Ordinary-light movement uses this Move-then-Rotate sequence.

**Production rule:** The writer rejects non-finite or invalid transform data and verifies that the requested final state was reached within bounded tolerances.

## Batch planning and failure behavior

**Observed:** A complete preflight rejection can produce zero writes.

**Observed:** A failure after mutation can leave partial authored state.

**Observed:** One immediate native Ctrl+Z recovered all tested partial states, including a case in which translation of a second light had occurred before its orientation restoration failed.

**Production rule:** The complete batch is planned before the first write.

**Production rule:** All selected writes use one native recording operation.

**Production rule:** On a post-write verification failure, the user is directed to perform one immediate Ctrl+Z.

**Limitation:** V1 does not implement a second reverse-write or fake Undo mechanism.

**Limitation:** Automatic rollback through unqualified abort APIs is not part of the release contract.

## Temporal and authored-state behavior

**Observed:** SFM exposes distinct script-operation time and visible UI-head time behavior.

**Observed:** Changing the visible head programmatically and then immediately reading the DAG in the same invocation did not synchronously reveal the visibly authored animation in the tested fixture.

**Observed:** Moving the UI head manually between separate read-only invocations exposed the existing animation.

**Observed:** In the T08X fixture, writing the light at frame 0 with the repaired Move-then-Rotate writer did not flatten or offset the tested later position samples at frames 4 and 6.

**Observed:** Orientation at the written sample was preserved within approximately `0.0000102453` degrees.

**Limitation:** Exact hidden key, layer, default-value, and interpolation representation was not inspected.

**Limitation:** General preservation of every possible pre-existing orientation animation was not proven.

**Production rule:** V1 is a current-shot initial-staging utility, primarily for short and effectively still clips. It does not claim to be an animation-retiming or curve-editing tool.

## Character-relative references

Bring Near uses a conservative reference hierarchy.

### BODY

**Production rule:** BODY is the preferred reference for full role placement.

A qualified BODY frame supplies the character-relative right, forward, and up directions and a torso-centered placement reference.

**Production rule:** Native Light Kit placement requires BODY qualification.

### BOUNDS and ROOT

**Production rule:** BOUNDS and ROOT are limited fallback references for placements that do not require a fully qualified character frame, such as Nearby Only.

They are not promoted into a guessed full-body orientation.

### Eyes and face reference

**Observed:** On the tested model, this call returned a live evaluated point:

```
gameModel.ComputeAttachmentPosition("eyes")
```

The point followed both whole-model movement and neck/head articulation.

**Observed:** The qualified ordinary-light path successfully used the exact `eyes` attachment on one tested character.

**Observed:** A strict paired-eye and head fallback succeeded on another tested character.

**Production rule:** Eye placement prefers an exact live eye attachment.

**Production rule:** Fallback requires the expected paired-eye and head structure. Weak name resemblance is insufficient.

**Limitation:** The attachment-position API proves a live point. It does not by itself establish a generally accessible full attachment world orientation.

## Role recognition and placement

**Production rule:** Role recognition is advisory.

Recognized names may suggest:

- Key;
- Fill;
- Backlight;
- Rim;
- Hair;
- Floor;
- Eye; or
- Background.

The artist can change the placement or leave the light unselected.

**Production rule:** Unknown lights can use Nearby Only.

**Production rule:** Multiple lights assigned to the same placement are staggered rather than written to exactly the same point.

**Production rule:** Flip affects only the model-relative lateral offset of Key, Fill, and Rim.

Flip does not change:

- role identity;
- forward offset;
- vertical offset;
- aim target;
- duplicate staggering; or
- placements outside Key, Fill, and Rim.

## Parent and relationship safety

Bring Near treats transform relationships as a safety property, not as a placement preference.

**Observed:** A light with an override parent can be identified through its DAG relationship state.

**Observed:** Moving a light can move a dependent object even when the reverse relationship is not visible through the light’s immediate parent state.

**Production rule:** Qualification performs bounded current-shot checks for both relationships affecting the light and detectable scene objects depending on the light.

**Production rule:** Unsupported or ambiguous relationships make the light unavailable.

**Production rule:** Parent identity is captured before writing and verified afterward.

**Limitation:** V1 does not recursively traverse arbitrary authored animation networks.

**Limitation:** A bounded public script cannot promise discovery of every possible hidden native dependency. When the supported checks cannot establish safety, the candidate fails closed.

## Native Light Kit architecture

SFM’s native Light Kit is not treated as four ordinary lights.

### Recognized structure

**Production rule:** Eligibility requires the expected native structure, including:

- one visible Light Kit owner animation set;
- a transform resolving to `lightRoot`;
- the expected hidden Key, Fill, Rim, and Bounce projected-light members;
- each expected member parented beneath the same root;
- a qualified BODY reference on the invoked model; and
- no detected unrelated visible scene animation-set DAG depending on the root.

An incomplete, duplicate, or ambiguous structure is unavailable.

### Chooser contract

**Production rule:** A supported native Light Kit appears as one fixed-placement row:

`Light Kit — Whole kit centered on model`

The row deliberately has no placement dropdown, no Light Kit-specific tooltip, and no dedicated Light Kit Help paragraph. The native kit is treated as one prebuilt lighting setup rather than four independently staged lights.

### Why hidden members are not moved independently

**Observed:** An individual hidden member could translate while refusing the following orientation write.

That produced a large final orientation error and invalidated the ordinary-light writer for hidden kit members.

**Production rule:** Bring Near never applies the ordinary Move-then-Rotate writer to those hidden members.

### Root translation

**Observed:** Translating `lightRoot` moved all four hidden members by the same world-space delta while preserving measured orientation and parent identity.

**Observed:** The members’ aim rays converged on `lightRoot`, supporting its interpretation as the setup’s authored focus point.

**Observed:** Translating `lightRoot` to the invoked character’s BODY torso center preserved the tested internal arrangement.

**Production rule:** Bring Near moves only `lightRoot`.

It re-resolves the expected members before writing and verifies:

- root destination;
- member translation;
- member orientation; and
- member parent identity.

### Collateral-movement protection

**Production rule:** Expected internal members are allowed beneath the kit root.

**Production rule:** An unrelated user-visible scene animation-set DAG detected beneath that root makes the whole kit unavailable.

This preserves the intended native setup while refusing a root move that would visibly carry unrelated authored scene content.

## Deep introspection boundary

**Observed:** Deep channel, log, layer, and key introspection caused a native SFM crash during development.

**Production rule:** That path remains quarantined.

The production tool does not require:

- recursive channel traversal;
- recursive log traversal;
- animation-layer inspection;
- hidden key enumeration; or
- an offline database.

A future version should not reopen this area without an isolated, independently justified need.

## Supported failure model

V1 fails closed when it cannot establish:

- current-shot identity;
- anchor identity;
- projected-light identity;
- exact writable transform control;
- finite evaluated transforms;
- a supported placement reference;
- relationship safety;
- stable post-chooser context;
- Light Kit structural identity; or
- successful post-write verification.

This conservatism is intentional. Leaving a light unmoved is preferable to moving authored scene content unexpectedly.

## Deliberate V1 limits

- Current shot only.
- Existing projected lights plus the supported native SFM Light Kit only.
- No camera movement.
- No generic root or name guessing.
- No Master or Normalizer dependency.
- No persistent background service.
- No per-frame service.
- No offline scanner or corpus dependency.
- No deep channel, log, layer, or key inspection.
- No general animation-editing guarantees.
- No synthetic reverse-move Undo.
- No automatic rollback contract.
- No claim of universal skeleton understanding.
