# Upstream issues from the November 2026 dataset

What in [2026-11.md](2026-11.md) points at the conventions or at the
conformance suite rather than at a framework, drafted here before filing.
Framework bugs go to the frameworks and are listed at the end.

| target | status | link | outcome |
| --- | --- | --- | --- |
| semantic-conventions-genai: string[] attributes as JSON strings | drafted | | |
| semantic-conventions-genai #187: per-step spans, two more data points | drafted | | |
| semantic-conventions-conformance: span kind check | drafted | | |
| #otel-genai-instrumentation post | drafted | | |

## semantic-conventions-genai: say that string[] attributes are arrays

Title: Say explicitly that string[] attributes are arrays, not JSON-encoded strings

Three independent instrumentations set `gen_ai.response.finish_reasons` to
a JSON-encoded string such as `"[\"stop\"]"` instead of a string array:

- Microsoft.Extensions.AI 10.11.0 (.NET): `OpenTelemetryChatClient` builds
  the value with `$"[\"{finishReason}\"]"`
  (`src/Libraries/Microsoft.Extensions.AI/ChatCompletion/OpenTelemetryChatClient.cs`).
- LiteLLM 1.106.2, native OpenTelemetry callback: `safe_dumps(finish_reasons)`
  (`litellm/integrations/opentelemetry.py`).
- Microsoft Agent Framework (Python): the conformance report flags
  `type_mismatch` on the same attribute for its `chat` and `invoke_agent`
  spans (`gen-ai/python/agent-framework/native`), and it flags LiteLLM native
  the same way.

The OTLP attribute model is clear and Weaver reports it as a type mismatch,
so the instrumentations are wrong. But three teams making the same choice
suggests the docs invite it: the examples column renders the values as
`["stop"]`, `["stop", "length"]`, which reads like JSON, and the messages
attributes next to it are documented as JSON strings. Nothing in the
attribute note says an array attribute has to stay an array.

Suggestion: add a sentence to the `gen_ai.response.finish_reasons` note
(and to `gen_ai.request.stop_sequences` and
`gen_ai.request.encoding_formats`, the other `string[]` attributes) saying
the value MUST be set as an array-typed attribute and that a JSON-encoded
string is not equivalent, since backends cannot index into it.

Found with spanlint, an offline linter for exported OTLP, over captures from
nine frameworks: https://github.com/inormis/spanlint/blob/main/docs/conformance/2026-11.md

## semantic-conventions-genai #187: comment

Two more data points for the per-step span discussion, from captures of
real frameworks:

- Vercel AI SDK 7.0.163 with `@ai-sdk/otel` 1.0.163 (`OpenTelemetry`
  integration, tracer `gen_ai`) emits `invoke_agent {model}` (INTERNAL),
  then `step N` (INTERNAL, `gen_ai.operation.name=agent_step`, no other
  attributes), then `chat {model}` (CLIENT). The step span is the
  per-iteration span from #81, not a workflow node, and the SDK had to
  invent an operation name for it.
- OpenLLMetry's LangChain instrumentation 0.62.4 emits
  `execute_task {node.name}` (INTERNAL, `gen_ai.operation.name=execute_task`)
  for a `ChatPromptTemplate` step inside a one-step chain, with
  `gen_ai.provider.name=langchain`. Same shape as the LangGraph case listed
  above.

So the gap is not only workflow nodes: an agent loop's iteration is the
other unit frameworks are reaching for. Whatever lands here, it would help
if the operation name for a unit of work that is neither an agent nor a
tool were spelled out, since both SDKs currently produce values outside the
enum and get reported as `genai_operation_name_unknown`.

Captures: https://github.com/inormis/spanlint/tree/main/tests/fixtures

## semantic-conventions-conformance: span kind

Title: Report span kind mismatches for GenAI spans

The GenAI span definitions carry a `kind` (CLIENT for inference,
embeddings, create_agent and the remote invoke_agent; INTERNAL for
execute_tool, plan and the in-process invoke_agent), and the live-check
sample span has the kind, but no finding in the current report covers it.
Two libraries get it wrong on their inference span:

- Semantic Kernel 1.45.0 (Python) starts `chat gpt-4o-mini` without a kind,
  so it is INTERNAL.
- LiteLLM 1.106.2 native callback starts `litellm_request` (operation
  `chat`) as INTERNAL.

LiteLLM native is already a target; Semantic Kernel is not. A
`span_kind_mismatch` advice in the GenAI policies would make this visible
on the report. Kind matters for backends: CLIENT spans are what drives
service maps and client-side latency panels.

Captures and numbers: https://github.com/inormis/spanlint/blob/main/docs/conformance/2026-11.md

## Dropped before filing

- JS integral doubles exported as ints: Weaver accepts an int where a double
  is declared since v0.23.0 (open-telemetry/weaver#1331, from #1323 filed
  for exactly this JS case), and the conformance suite closed its workaround
  issue (#9). spanlint now does the same. Nothing to file.
- Vercel's invoke_agent carrying request attributes: the conventions
  recommend them on invoke_agent, and #697 already tracks revisiting that.

## Framework bugs, to file with the frameworks

- Semantic Kernel (Python) 1.45.0: chat span INTERNAL; `gen_ai.system`
  instead of `gen_ai.provider.name`; temperature 0 dropped as falsy.
- LiteLLM 1.106.2 native callback: chat span INTERNAL; finish_reasons as a
  JSON string; `gen_ai.system` and `gen_ai.openai.response.service_tier`
  instead of the current names; no `gen_ai.provider.name`.
- Microsoft.Extensions.AI 10.11.0: finish_reasons as a JSON string.
- Vercel AI SDK 7.0.163 / @ai-sdk/otel 1.0.163: `LegacyOpenTelemetry` sets
  `gen_ai.system=openai.chat`; the `OpenTelemetry` integration puts
  `gen_ai.client.operation.duration`, a metric name, on the chat span as an
  attribute; `agent_step` (see the #187 comment).
- OpenLLMetry LangChain 0.62.4: `gen_ai.provider.name=langchain` on the
  workflow and task spans, where the conventions have no provider;
  `execute_task` (see the #187 comment).
- opentelemetry-instrumentation-openai-v2 2.4b0: the default output still
  uses `gen_ai.system`; `gen_ai.provider.name` only with
  `OTEL_SEMCONV_STABILITY_OPT_IN=gen_ai_latest_experimental`. By design, not
  a bug, but worth knowing.

## SIG post

For #otel-genai-instrumentation:

> Hi all. I have been building spanlint, a small offline linter for GenAI
> telemetry: point it at an OTLP JSON export (or use its pytest fixture)
> and it reports where the spans diverge from the GenAI conventions. It is
> deliberately the other end of the pipe from the conformance suite: no
> scenario, no mock server, just whatever a framework actually exported. So
> it covers a few things the suite does not yet (.NET
> Microsoft.Extensions.AI, Semantic Kernel, Langfuse, Traceloop decorators)
> and it checks span kind.
>
> First dataset over nine frameworks, registry pinned to
> semantic-conventions-genai e6658f1:
> https://github.com/inormis/spanlint/blob/main/docs/conformance/2026-11.md
>
> Two things that look like doc gaps rather than framework bugs went to the
> genai repo (<issue link> and a comment on #187); a span-kind check
> suggestion went to the conformance repo (<issue link>). Happy to adjust
> the rules if any reading of the spec is off.
>
> Repo: https://github.com/inormis/spanlint
