# spanlint

Checks whether GenAI telemetry actually matches the OpenTelemetry GenAI
semantic conventions.

Most AI frameworks now emit OpenTelemetry spans for model calls, and the
[GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
say what those spans are supposed to contain. The two do not always agree.
Attributes get left out. Old names stick around long after the spec renames
them. Token metrics turn up without the right unit. Required events are
missing entirely.

You normally find this out from a dashboard, when a panel is empty and
nobody can say which layer dropped the attribute.

spanlint reads the telemetry a framework really emits and reports where it
diverges from the spec.

## Not Weaver

[Weaver](https://github.com/open-telemetry/weaver) works on the convention
registries: the YAML that defines what an attribute is, and code generation
from it. spanlint looks at the other end, the spans and metrics a running
application produces. If you are writing conventions, you want Weaver. If
you are checking whether your instrumentation follows them, this.

## Supported frameworks

Framework detection is what tells spanlint which spans came from where, so
per-framework conformance can be reported without mixing everything together.

- **openai-python**: spans emitted directly by the OpenAI Python SDK, and
  by the OpenTelemetry contrib instrumentation
  (`opentelemetry-instrumentation-openai`, including the `_v2` scope).
  Identification falls back to `gen_ai.system=openai` when the instrumentation
  scope name is not one of the expected values.

More adapters land as work on them starts.

## Status

Early, but it runs. You can feed it an OTLP JSON export and get a list of
findings back, in text or JSON. There are a dozen rules so far, all for the
GenAI conventions: attribute types, the operation name enum, the two
message/choice events, and the token/duration histograms. The only
framework it recognises today is the OpenAI Python SDK. There is also a
pytest fixture that grabs whatever spans your test emits so you can lint
them in place.

Nothing is on PyPI yet. 0.1.0 is cut in the changelog and goes out as soon
as the publishing side is wired up. After that: a proper `spanlint check`
subcommand, more framework adapters, and a report that shows per framework
where the telemetry drifts from the spec.

Apache-2.0