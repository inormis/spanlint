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

## Not Weaver, not the conformance suite

[Weaver](https://github.com/open-telemetry/weaver) works on the convention
registries: the YAML that defines what an attribute is, code generation from
it, and, with `weaver registry live-check`, validation of sample telemetry
against them. The OpenTelemetry project runs that live-check over scenario
programs for several dozen GenAI library and instrumentation pairs in
[semantic-conventions-conformance](https://github.com/open-telemetry/semantic-conventions-conformance)
and publishes the results. If you maintain an instrumentation, that is where
its conformance is tracked.

spanlint is for the other side. You have an application, it exports
telemetry, and you want to know in CI whether what it exports still matches
the conventions. It reads OTLP JSON files or captures spans in a pytest
fixture, needs no mock server and no scenario, and tells you which spans
came from which framework. It also carries a few checks the suite does not
have today, span kind among them, and fixtures from runtimes the suite does
not run (.NET, Node). The first comparison across nine frameworks is in
[docs/conformance/2026-11.md](docs/conformance/2026-11.md).

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

`spanlint matrix <dir>` runs the bundled framework adapters over a tree of
exports laid out as `<dir>/<framework>/*.json` and prints a markdown table
of finding counts per framework and rule. The fixtures in this repository
are laid out that way, so `spanlint matrix tests/fixtures` reproduces the
table in [docs/conformance/2026-11.md](docs/conformance/2026-11.md).

## Use in CI

In GitHub Actions, [spanlint-action](https://github.com/inormis/spanlint-action)
installs spanlint and checks a set of OTLP exports, for example the traces
your integration tests write through the Collector's file exporter:

```yaml
- uses: inormis/spanlint-action@v1
  with:
    files: traces/**/*.json
```

Findings show up as warnings on the files and in the job summary, and the
step fails if there are any.

## Supported frameworks

Framework detection is what tells spanlint which spans came from where, so
per-framework conformance can be reported without mixing everything together.

- **openai-python**: spans from the OpenTelemetry contrib instrumentation
  (`opentelemetry-instrumentation-openai-v2`, scope
  `opentelemetry.instrumentation.openai_v2`) and from Traceloop's OpenAI
  instrumentation (scope `opentelemetry.instrumentation.openai.v1`).
  Identification falls back to `gen_ai.system=openai` or
  `gen_ai.provider.name=openai` when the scope name is not one of the
  expected values; that is also how the contrib instrumentation's
  `gen_ai_latest_experimental` output is recognised, since that path emits
  from opentelemetry-util-genai's own `opentelemetry.util.genai.handler`
  scope.
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
- **Microsoft.Extensions.AI** (.NET): spans from the library's
  `UseOpenTelemetry` chat client, which puts them on the
  `Experimental.Microsoft.Extensions.AI` activity source unless the
  application names its own. Scope name only. The attributes are plain
  `gen_ai.*`, so a span from a renamed source goes unrecognised.
- **Vercel AI SDK** (Node): spans from `@ai-sdk/otel`, which is where AI
  SDK 7 keeps its OpenTelemetry support. Its `OpenTelemetry` integration
  puts the `invoke_agent`, `agent_step` and `chat` spans on a tracer named
  `gen_ai`; the `LegacyOpenTelemetry` one puts the older `ai.generateText`
  spans on a tracer named `ai`. Either scope name counts. A legacy span under
  an application-supplied tracer is still recognised by its `ai.operationId`
  attribute; a semconv one carries nothing of the SDK's own, so it is not.
- **Langfuse**: spans from the Langfuse Python SDK, which is built on
  OpenTelemetry and puts everything it emits, the `@observe` decorator and
  its OpenAI and LangChain integrations included, on one tracer named
  `langfuse-sdk`. Scope name only. The `langfuse.*` attributes are no help
  because the SDK also copies propagated ones onto third-party spans.
- **Traceloop SDK**: the workflow, task, agent and tool spans that the
  `traceloop-sdk` decorators emit under the `traceloop.tracer` scope. Spans
  from Traceloop's per-framework instrumentations are claimed by the
  framework adapters above, not by this one.

More adapters land as work on them starts.

## Status

Early, but it runs. You can feed it an OTLP JSON export and get a list of
findings back, in text or JSON. The rules follow the GenAI conventions as
of November 2026 (the registry is pinned to a semantic-conventions-genai
commit, see `scripts/refresh_registry.sh`): `gen_ai.operation.name` on
every GenAI span and `gen_ai.provider.name` where the span definitions
require it, renamed and removed attribute names,
the open operation name enum, span kind per operation, attribute types,
the two legacy message/choice events, and the token/duration histograms.
It recognises spans from the OpenAI contrib instrumentation, LangChain,
LlamaIndex, LiteLLM, Semantic Kernel, Microsoft.Extensions.AI, the Vercel
AI SDK, Langfuse and the Traceloop SDK, and `spanlint matrix` turns a tree
of exports into the per-framework table in `docs/conformance/`. There is
also a pytest fixture that grabs whatever spans your test emits so you can
lint them in place.

On PyPI as of 0.2.0, and runs in GitHub Actions through
[spanlint-action](https://github.com/inormis/spanlint-action). Next up: a
second dataset once the conventions move again.

Apache-2.0