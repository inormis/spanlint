# spanlint

[spanlint](https://github.com/inormis/spanlint) checks whether the
telemetry an AI framework emits matches the
[OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/).

## Conformance datasets

- [November 2026](conformance/2026-11.md): nine frameworks across Python,
  .NET and Node, one scripted model call each. Every one of them diverges
  from the conventions somewhere.

Each dataset is regenerated from the captures in the repository with
`spanlint matrix tests/fixtures`.

## Use it

```
pip install spanlint
spanlint check trace.json
```

In GitHub Actions: [spanlint-action](https://github.com/inormis/spanlint-action).
