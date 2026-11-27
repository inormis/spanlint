# Changelog

## 0.2.1 — 2026-11-27

No changes to the linter itself.

### Added
- [spanlint-action](https://github.com/inormis/spanlint-action) runs spanlint
  in GitHub Actions. The README has a short "Use in CI" section, and the
  `action-selftest` workflow checks the action against the fixtures here.
- The conformance dataset is published as a page at
  https://inormis.github.io/spanlint/.
- `CITATION.cff`, so the repository and the dataset can be cited. The release
  is archived on Zenodo.

## 0.2.0 — 2026-11-17

First published release. 0.1.0 was tagged locally but never went out, so this
entry covers everything spanlint does today.

### Added
- Span and metric models, and an OTLP reader: JSON exports, line-delimited
  JSONL, and an OTLP/HTTP receiver for runtimes whose exporters only speak
  protobuf.
- Registry loader for the OpenTelemetry GenAI semantic conventions, reading
  both `groups` and Weaver `definition/2` files. The shipped registry is
  `model/gen-ai/registry.yaml` from open-telemetry/semantic-conventions-genai,
  pinned to a commit and refreshed by `scripts/refresh_registry.sh`.
- Span rules: `gen_ai.operation.name` required and checked against the open
  enum, `gen_ai.provider.name` required per operation, deprecated attribute
  names, span kind per operation, attribute type checks, and
  `gen_ai.attributes.missing` for framework spans that carry no `gen_ai.*`
  attribute at all.
- Event rules for `gen_ai.user.message`, `gen_ai.system.message` and
  `gen_ai.choice`. Metric rules for `gen_ai.client.token.usage` and
  `gen_ai.client.operation.duration`.
- Framework adapters for nine instrumentations across Python, .NET and Node:
  OpenAI, LangChain, LlamaIndex, Traceloop/OpenLLMetry, LiteLLM, Semantic
  Kernel, Langfuse, Microsoft.Extensions.AI and the Vercel AI SDK.
- `spanlint check <path>` for one export and `spanlint matrix <dir>` for a
  per-framework conformance table. Text and JSON reports.
- pytest plugin: the `spanlint_spans` fixture captures the spans a test emits
  so they can be linted in place.
- First conformance dataset, `docs/conformance/2026-11.md`: nine frameworks
  audited against the November registry, with capture scripts, pinned
  versions and per-framework notes.

### Changed
- `gen_ai.system` is gone from the conventions. The rule that required it was
  replaced by `gen_ai.provider.name.required`, and `gen_ai.system` is now
  reported as a deprecated name.
- An integer is accepted where the conventions declare a double, matching
  Weaver since v0.23.0.
