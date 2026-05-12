# Shared Contracts

The single most important document in this folder. Without versioned, shared types, AGON + KAIROS + DIALECTICA produce inconsistent graphs and integration rots in months.

> **Status.** Draft v0.1. Schema is **specified** here; the `tacitus-contracts` package is **not yet published**. Implementation tracked in [`ROADMAP.md`](./ROADMAP.md) §1.

---

## Why contracts

Three services, three languages, three teams of one (today, more later). Each currently mints its own ActorID format, its own span schema, its own enum vocabularies. Fusion at ingestion time becomes string-matching guesswork.

The fix: **one schema, three language bindings, one versioning lifecycle.**

---

## Package layout

```
tacitus-contracts/
├── schema/
│   ├── identifiers.proto
│   ├── source.proto
│   ├── actor.proto
│   ├── event.proto
│   ├── claim.proto
│   ├── commitment.proto
│   ├── contradiction.proto
│   └── envelope.proto
├── codegen/
│   ├── rust/      (cargo workspace member)
│   ├── python/    (uv package)
│   └── typescript/(npm package)
├── docs/
│   └── changelog.md
└── README.md
```

Hosted as a separate GitHub repo (`sargonxg/tacitus-contracts`) or as a workspace member in DIALECTICA monorepo. Decision tracked in [`ROADMAP.md`](./ROADMAP.md).

**Tooling decision (TBD):** protobuf vs JSON Schema. Recommend protobuf for performance + first-class Rust support. JSON Schema fallback if cross-language tooling friction.

---

## Core types

### Identifiers

```proto
// All IDs are UUID v7 strings (sortable, timestamp-prefixed).
// Format: "<entity-prefix>_<uuid7>" — prefix lets humans distinguish ID types.

message ActorId   { string value = 1; } // "act_018f..."
message EventId   { string value = 1; } // "evt_018f..."
message ClaimId   { string value = 1; } // "clm_018f..."
message DocumentId{ string value = 1; } // "doc_018f..."
message WorkspaceId{string value = 1; } // "ws_018f..."
message SpanId    { string value = 1; } // "spn_018f..."
```

**Who mints:**
| Type | Owner |
|---|---|
| `DocumentId` | DIALECTICA (on ingestion) |
| `WorkspaceId` | DIALECTICA |
| `ActorId` (canonical) | DIALECTICA (resolves AGON + KAIROS local IDs to canonical at fusion) |
| `EventId` (canonical) | KAIROS |
| `ClaimId` | AGON |
| `SpanId` | service that produced the span; DIALECTICA preserves as foreign key |

### SourceSpan

The atomic citation unit. Every claim, event, commitment, actor mention must carry one.

```proto
message SourceSpan {
  SpanId id = 1;
  DocumentId document_id = 2;
  int64 char_start = 3;       // UTF-8 byte offset start
  int64 char_end = 4;         // UTF-8 byte offset end (exclusive)
  string text = 5;            // verbatim slice, for verification
  string sha256 = 6;           // hash of `text` for tamper detection
  optional int32 segment_id = 7;  // KAIROS segmentation reference, if any
  ConfidenceMarker confidence = 8;
}

enum ConfidenceMarker {
  CONFIDENCE_UNSPECIFIED = 0;
  EXACT = 1;        // span text matches document slice byte-for-byte
  NORMALIZED = 2;   // span text matches after whitespace/case normalization
  UNRESOLVED = 3;   // could not be matched back to source
}
```

**Rule:** any node referencing a span MUST resolve to `EXACT` or `NORMALIZED` for production graph writes. `UNRESOLVED` spans are stored but flagged and not eligible for reasoning.

### Actor

```proto
message Actor {
  ActorId id = 1;                  // canonical (DIALECTICA-minted)
  string canonical_name = 2;
  ActorType type = 3;              // PERSON | ORG | STATE | COALITION | ROLE
  repeated string aliases = 4;
  optional ActorId merged_from_kairos = 5;  // KAIROS-local ID, kept for trace
  optional ActorId merged_from_agon = 6;    // AGON-local ID, kept for trace
  repeated SourceSpan mentions = 7;
}

enum ActorType {
  ACTOR_TYPE_UNSPECIFIED = 0;
  PERSON = 1;
  ORG = 2;
  STATE = 3;
  COALITION = 4;
  ROLE = 5;  // reified role: "the claimant", "the mediator"
}
```

**Alias resolution rule:** AGON's `aco-fuse` deterministic normalizer + KAIROS's actor registry both emit candidate canonical names. DIALECTICA's fusion layer reconciles using:
1. Exact canonical match → merge.
2. Fuzzy match (Levenshtein ≤ 2 + same `type`) → flag for human review unless workspace has `auto_merge_threshold` set.
3. No match → new Actor.

### Event

KAIROS owns this type. DIALECTICA imports.

```proto
message Event {
  EventId id = 1;
  string canonical_label = 2;
  optional Timestamp timestamp = 3;
  Fuzziness fuzziness = 4;
  repeated ActorId participants = 5;
  repeated SourceSpan spans = 6;
  optional PloverType plover_type = 7;  // 16-type taxonomy (DIALECTICA-defined)
  optional int32 severity = 8;          // 1-10, DIALECTICA-defined
}

message Timestamp {
  optional int64 unix_seconds = 1;
  optional string iso8601 = 2;          // preserves original precision
  DateResolution resolution = 3;        // YEAR | MONTH | DAY | HOUR | MINUTE
}

enum Fuzziness {
  FUZZ_EXACT = 0;     // "January 15, 2024"
  FUZZ_APPROX = 1;    // "mid-January 2024"
  FUZZ_RELATIVE = 2;  // "three weeks later"
  FUZZ_UNRESOLVED = 3;// could not anchor
}

enum DateResolution {
  RES_UNSPECIFIED = 0;
  YEAR = 1;
  MONTH = 2;
  DAY = 3;
  HOUR = 4;
  MINUTE = 5;
}
```

### AllenRelation

KAIROS computes these between Events and Episodes.

```proto
message AllenRelation {
  oneof subject {
    EventId event_id = 1;
    EpisodeId episode_id = 2;
  }
  oneof object {
    EventId obj_event = 3;
    EpisodeId obj_episode = 4;
  }
  AllenType type = 5;
}

enum AllenType {
  BEFORE = 0;
  AFTER = 1;
  MEETS = 2;
  MET_BY = 3;
  OVERLAPS = 4;
  OVERLAPPED_BY = 5;
  STARTS = 6;
  STARTED_BY = 7;
  DURING = 8;
  CONTAINS = 9;
  FINISHES = 10;
  FINISHED_BY = 11;
  EQUALS = 12;
}
```

### Claim

AGON owns this type. DIALECTICA imports.

```proto
message Claim {
  ClaimId id = 1;
  ActorId subject = 2;          // who is making the claim
  string predicate = 3;         // verb-phrase, controlled vocabulary TBD
  oneof object {
    ActorId actor_object = 4;
    EventId event_object = 5;
    string string_object = 6;
  }
  repeated SourceSpan evidence = 7;
  VerificationStatus verification = 8;
  optional float confidence = 9;     // 0.0-1.0
  optional string contradicted_by = 10;  // ClaimId of contradicting claim, if any
}

enum VerificationStatus {
  STATUS_UNSPECIFIED = 0;
  VERIFIED = 1;       // evidence span exists and matches source
  UNRESOLVED = 2;     // no evidence span recovered
  CONTRADICTED = 3;   // another claim disputes this one
  DENIED = 4;         // explicit denial extracted from source
}
```

### Commitment

KAIROS owns. DIALECTICA preserves state machine.

```proto
message Commitment {
  string id = 1;
  ActorId committer = 2;
  ActorId target = 3;            // who the commitment is to
  string content = 4;            // free text of what was committed
  CommitmentState state = 5;
  optional Timestamp deadline = 6;
  optional Timestamp committed_at = 7;
  repeated SourceSpan evidence = 8;
}

enum CommitmentState {
  STATE_UNSPECIFIED = 0;
  PLEDGED = 1;     // initial state
  ACTIVE = 2;      // accepted, in progress
  FULFILLED = 3;   // completed
  BREACHED = 4;    // failed / deadline passed without fulfillment
  CONTESTED = 5;   // disputed by another actor
  WITHDRAWN = 6;   // committer withdrew
}
```

### Contradiction

AGON owns.

```proto
message Contradiction {
  string id = 1;
  ClaimId claim_a = 2;
  ClaimId claim_b = 3;
  ContradictionMechanism mechanism = 4;
  int32 severity = 5;            // 1-5
  optional float confidence = 6;
  string explanation = 7;        // short rationale, human-readable
}

enum ContradictionMechanism {
  MECH_UNSPECIFIED = 0;
  DIRECT_NEGATION = 1;       // "X happened" vs "X did not happen"
  DATE_INCONSISTENCY = 2;
  ATTRIBUTION_DISPUTE = 3;   // who did/said it
  OBLIGATION_DENIAL = 4;     // "I committed" vs "I never committed"
  SEMANTIC = 5;              // model-suggested only, lower confidence
}
```

### Envelope (transport)

Every cross-service call uses this wrapper.

```proto
message AnalysisEnvelope {
  string contracts_version = 1;  // "1.0.0"
  string trace_id = 2;
  WorkspaceId workspace_id = 3;
  DocumentId document_id = 4;
  string source_service = 5;     // "dialectica" | "kairos" | "agon"
  google.protobuf.Timestamp produced_at = 6;
}

message KairosOutput {
  AnalysisEnvelope envelope = 1;
  repeated Actor actors = 2;
  repeated Event events = 3;
  repeated Commitment commitments = 4;
  repeated AllenRelation relations = 5;
  // ... episodes, hypotheses, friction etc.
}

message AgonOutput {
  AnalysisEnvelope envelope = 1;
  repeated Actor actors = 2;
  repeated Claim claims = 3;
  repeated Contradiction contradictions = 4;
  // ... friction matrix, quality gates, etc.
}
```

---

## Compatibility rules

1. **Additive changes only within a major version.** New optional fields = minor bump. New required fields = major bump.
2. **No field reuse.** Once a field number is published, it's gone forever (protobuf discipline).
3. **Enums must keep `_UNSPECIFIED = 0` as default.** Lets old clients tolerate new values.
4. **Field deprecation, never removal.** Mark with `[deprecated = true]`, keep emitting for one major version.
5. **Every service declares range:** `contracts: ">=1.0.0, <2.0.0"` in its manifest.

### Compatibility check at runtime

DIALECTICA's gateway checks contracts version on every cross-service call:
- KAIROS responds with `envelope.contracts_version`.
- If outside declared range → log error, skip enrichment, continue pipeline.
- If within range → proceed.

---

## Tooling

### Code generation

```
schema/*.proto
    │
    ├── codegen/rust/      (prost + tonic if gRPC, prost-build for plain)
    ├── codegen/python/    (protobuf + mypy stubs)
    └── codegen/typescript/(ts-proto)
```

CI in `tacitus-contracts` runs on every PR:
1. `buf lint` — schema discipline.
2. `buf breaking --against main` — block incompatible changes.
3. Regenerate all three language packages.
4. Publish on tag push.

### Local override during development

Until `tacitus-contracts` is published, DIALECTICA can use a workspace path dependency:
```toml
# packages/api/pyproject.toml
dependencies = [
  "tacitus-contracts @ file://../../../tacitus-contracts/codegen/python",
]
```

---

## Open questions (to resolve before v1.0.0)

1. **Predicate vocabulary for Claims.** AGON currently uses free strings. Should we have a controlled set? Risk: ontology lock-in. Mitigation: start free, observe top-N, formalize in v1.1.
2. **PloverType ownership.** Currently in DIALECTICA ontology. Should it move to contracts so KAIROS can emit it directly? Recommend: yes, in v1.1.
3. **Episode primitive.** KAIROS has it; not yet in this spec. Add in v0.2.
4. **PowerDynamic, EmotionalState, TrustState** — DIALECTICA-specific or shared? Recommend: DIALECTICA-only for now (none of the three services need to share them as inputs).
5. **Streaming spec.** Should AGON/KAIROS support streaming output via SSE/gRPC streaming? Pipeline benefits from progressive disclosure. Recommend: yes, defer to v1.2.

---

## Implementation checklist

- [ ] Decide protobuf vs JSON Schema
- [ ] Create `tacitus-contracts` repo (or workspace member)
- [ ] Write schema files for v0.1.0 (types above)
- [ ] Generate Rust + Python + TypeScript bindings
- [ ] Wire `buf` CI checks
- [ ] DIALECTICA: replace inline types with `tacitus-contracts` imports for new code paths
- [ ] AGON: add `tacitus-contracts` Cargo dep, mirror `aco-core` types
- [ ] KAIROS: add `tacitus-contracts` Cargo dep, mirror `kairos-core` types
- [ ] Document migration path for existing in-repo types
- [ ] Publish v0.1.0 to PyPI/crates.io/npm
- [ ] Tag v1.0.0 after first end-to-end pipeline run with real data

---

*This document is the contract. Edit carefully.*
