# spanlint

Checks whether GenAI telemetry actually matches the OpenTelemetry GenAI
semantic conventions.

Most AI frameworks now emit OpenTelemetry spans for model calls, and the
[GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
say what those spans are supposed to contain. The two do not always agree.
Attributes get left out. Old names stick around long after the spec renames
them. Token metrics turn up withot the right unit. Required events are
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

## Status

Nothing works yet. No release, no CLI, no API. Currently building the span
model and the first validation rules.

Apache-2.0