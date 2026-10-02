# Changelog

## 0.1.0 — 2026-10-02

First release.

### Added
- Span and Metric data models.
- Loader for OpenTelemetry semantic convention YAML (attribute groups).
- `validate()` and `validate_metrics()` runners returning `Finding` records.
- Attribute rules: `gen_ai.system` required on GenAI-shaped spans,
  `gen_ai.operation.name` enum, type checks for `gen_ai.request.model`,
  `gen_ai.response.model`, `gen_ai.request.temperature`,
  `gen_ai.request.top_p`, `gen_ai.request.max_tokens`,
  `gen_ai.response.id`, `gen_ai.response.finish_reasons`.
- Event rules: type checks for attributes on `gen_ai.user.message`,
  `gen_ai.system.message` and `gen_ai.choice`.
- Metric rules: `gen_ai.client.token.usage` and
  `gen_ai.client.operation.duration` validated as histograms with the
  expected units.
- JSON and text report renderers.
- `spanlint` CLI with `--version` and `--format text|json`.
- OTLP JSON file parser producing `Span` objects.
- OpenAI SDK adapter: `is_openai_span` detects spans emitted by
  `openai-python` instrumentations.
