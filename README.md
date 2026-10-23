# spanlint

[![ci](https://github.com/inormis/spanlint/actions/workflows/ci.yml/badge.svg)](https://github.com/inormis/spanlint/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/spanlint.svg)](https://pypi.org/project/spanlint/)

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

## Install

```
pip install spanlint
```

## Usage

Point `spanlint check` at an OTLP JSON export of your telemetry:

```
$ spanlint check trace.json
no findings
```

Divergences from the GenAI conventions show up as one line each, with the
target span, the message, and the rule name:

```
$ spanlint check broken.json
chat: gen_ai.request.model must be a string [gen_ai.request.model.type]
1 finding
```

The exit code is nonzero whenever there are findings, so this fits a CI
step. Pass `--format json` for a machine-readable report:

```
$ spanlint check trace.json --format json
{
  "findings": []
}
```

Line-delimited OTLP exports (`.jsonl`, one export per line, which is what
the OTel Collector's file exporter writes) are read the same way. The
parser is picked by the file's extension.

## Supported frameworks

Framework detection is what tells spanlint which spans came from where, so
per-framework conformance can be reported without mixing everything together.

- **openai-python**: spans emitted directly by the OpenAI Python SDK, by
  the OpenTelemetry contrib instrumentation
  (`opentelemetry-instrumentation-openai`, including the `_v2` scope), and
  by Traceloop's OpenAI instrumentation (scope
  `opentelemetry.instrumentation.openai.v1`). Identification falls back to
  `gen_ai.system=openai` or `gen_ai.provider.name=openai` when the
  instrumentation scope name is not one of the expected values.
- **LangChain**: spans emitted by Traceloop's
  `opentelemetry-instrumentation-langchain`, which is also what the Traceloop
  SDK installs, and by Arize's `openinference-instrumentation-langchain`.
  Identification falls back to `gen_ai.provider.name` being `langchain` or
  `langgraph` when the scope name is not one of those.
- **LlamaIndex**: spans from LlamaIndex's own OpenTelemetry bridge
  (`llama-index-observability-otel`), from Traceloop's
  `opentelemetry-instrumentation-llamaindex`, and from Arize's
  `openinference-instrumentation-llama-index`. Scope name only; none of
  the three puts a LlamaIndex-specific attribute on every span.
- **LiteLLM**: spans from LiteLLM's own OpenTelemetry callback (tracer name
  `litellm`), from Traceloop's `opentelemetry-instrumentation-litellm`, and
  from Arize's `openinference-instrumentation-litellm`. Scope name only.
- **Semantic Kernel** (Python): spans from Semantic Kernel's own telemetry,
  which is off until `SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS`
  is set. Every tracer there is named after its module, so any scope starting
  with `semantic_kernel.` counts.
- **Traceloop SDK**: the workflow, task, agent and tool spans that the
  `traceloop-sdk` decorators emit under the `traceloop.tracer` scope. Spans
  from Traceloop's per-framework instrumentations are claimed by the
  framework adapters above, not by this one.

More adapters land as work on them starts.

## Status

Early, but it runs. You can feed it an OTLP JSON export and get a list of
findings back, in text or JSON. There are a dozen rules so far, all for the
GenAI conventions: attribute types, the operation name enum, the two
message/choice events, and the token/duration histograms. It recognises
spans from the OpenAI Python SDK, LangChain, LlamaIndex, LiteLLM, Semantic
Kernel and the Traceloop SDK. There is also a pytest fixture that grabs
whatever spans your test emits so you can lint them in place.

Nothing is on PyPI yet. 0.1.0 is cut in the changelog and goes out as soon
as the publishing side is wired up. After that: more framework adapters,
and a report that shows per framework where the telemetry drifts from the
spec.

Apache-2.0