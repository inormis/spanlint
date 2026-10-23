# Fixture capture versions

Every fixture under `tests/fixtures/<framework>/` was produced by the
script in `scripts/fixtures/<framework>/`. This file records the versions
that were installed when each capture was made, so a fixture can be
regenerated or compared against a newer release of the same framework.

## langchain

Captured 2026-10-15 with Python 3.12.13.

| package | version |
| --- | --- |
| langchain-core | 1.6.10 |
| langchain-openai | 1.7.1 |
| openai | 3.29.0 |
| opentelemetry-instrumentation-langchain | 0.62.4 |
| opentelemetry-semantic-conventions-ai | 0.5.1 |
| opentelemetry-sdk | 1.45.1 |
| opentelemetry-exporter-otlp-proto-common | 1.45.1 |

```
uv venv --python 3.12 .venv-langchain
uv pip install --python .venv-langchain/bin/python \
    langchain-core==1.6.10 langchain-openai==1.7.1 \
    opentelemetry-instrumentation-langchain==0.62.4 \
    opentelemetry-sdk==1.45.1 opentelemetry-exporter-otlp-proto-common==1.45.1
OPENAI_API_KEY=... .venv-langchain/bin/python scripts/fixtures/langchain/capture.py \
    > tests/fixtures/langchain/chain.json
```

The instrumentation is Traceloop's (OpenLLMetry); upstream
opentelemetry-python-contrib has no LangChain instrumentation at the time
of capture.

## llamaindex

Captured 2026-10-17 with Python 3.12.13. Two runs of the same script, one per
instrumentation.

| package | version |
| --- | --- |
| llama-index-core | 0.14.25 |
| llama-index-instrumentation | 0.5.0 |
| llama-index-llms-openai | 0.8.3 |
| llama-index-observability-otel | 0.7.0 |
| openai | 2.54.0 |
| opentelemetry-instrumentation-llamaindex | 0.62.4 |
| opentelemetry-instrumentation-openai | 0.62.4 |
| opentelemetry-semantic-conventions-ai | 0.5.1 |
| opentelemetry-sdk | 1.45.1 |
| opentelemetry-exporter-otlp-proto-common | 1.45.1 |

```
uv venv --python 3.12 .venv-llamaindex
uv pip install --python .venv-llamaindex/bin/python \
    llama-index-core==0.14.25 llama-index-llms-openai==0.8.3 \
    llama-index-observability-otel==0.7.0 \
    opentelemetry-instrumentation-llamaindex==0.62.4 \
    opentelemetry-instrumentation-openai==0.62.4 \
    opentelemetry-sdk==1.45.1 opentelemetry-exporter-otlp-proto-common==1.45.1
OPENAI_API_KEY=... .venv-llamaindex/bin/python scripts/fixtures/llamaindex/capture.py native \
    > tests/fixtures/llamaindex/chat_engine_native.json
OPENAI_API_KEY=... .venv-llamaindex/bin/python scripts/fixtures/llamaindex/capture.py traceloop \
    > tests/fixtures/llamaindex/chat_engine_traceloop.json
```

Under Traceloop the OpenAI call inside LlamaIndex is traced by Traceloop's
OpenAI instrumentation (scope opentelemetry.instrumentation.openai.v1), not
by the LlamaIndex one, so the traceloop file carries spans from two scopes.

## traceloop

Captured 2026-10-21 with Python 3.12.13.

| package | version |
| --- | --- |
| traceloop-sdk | 0.62.4 |
| openai | 3.35.1 |
| opentelemetry-instrumentation-openai | 0.62.4 |
| opentelemetry-semantic-conventions-ai | 0.5.1 |
| opentelemetry-sdk | 1.45.1 |
| opentelemetry-exporter-otlp-proto-common | 1.45.1 |

```
uv venv --python 3.12 .venv-traceloop
uv pip install --python .venv-traceloop/bin/python \
    traceloop-sdk==0.62.4 openai==3.35.1 httpx \
    opentelemetry-sdk==1.45.1 opentelemetry-exporter-otlp-proto-common==1.45.1
OPENAI_API_KEY=... .venv-traceloop/bin/python scripts/fixtures/traceloop/capture.py \
    > tests/fixtures/traceloop/workflow.json
```

httpx is listed because traceloop-sdk imports it without declaring it and
openai 3.x no longer depends on it. The run enables only the OpenAI
instrument, so the file has the SDK's workflow and task spans plus one
openai.chat span from opentelemetry-instrumentation-openai.

## litellm

Captured 2026-10-23 with Python 3.12.13. Two runs of the same script, one per
instrumentation.

| package | version |
| --- | --- |
| litellm | 1.106.2 |
| openai | 2.54.0 |
| opentelemetry-instrumentation-litellm | 0.62.4 |
| opentelemetry-semantic-conventions-ai | 0.5.1 |
| opentelemetry-sdk | 1.45.1 |
| opentelemetry-exporter-otlp-proto-common | 1.45.1 |

```
uv venv --python 3.12 .venv-litellm
uv pip install --python .venv-litellm/bin/python \
    litellm==1.106.2 opentelemetry-instrumentation-litellm==0.62.4 \
    opentelemetry-sdk==1.45.1 opentelemetry-exporter-otlp-proto-common==1.45.1
OPENAI_API_KEY=... .venv-litellm/bin/python scripts/fixtures/litellm/capture.py native \
    > tests/fixtures/litellm/completion_native.json
OPENAI_API_KEY=... .venv-litellm/bin/python scripts/fixtures/litellm/capture.py traceloop \
    > tests/fixtures/litellm/completion_traceloop.json
```

The native run uses LiteLLM's own OpenTelemetry callback (tracer name
litellm). It warns that the proxy server is not installed; that only skips
the proxy-specific hookup and the SDK callback still emits its spans. The
script blanks the OpenAI organisation and project headers and the Cloudflare
cookie that LiteLLM copies into hidden_params, since they identify the
account that made the capture.

## semantic_kernel

Captured 2026-10-23 with Python 3.12.13.

| package | version |
| --- | --- |
| semantic-kernel | 1.45.0 |
| openai | 3.37.0 |
| opentelemetry-sdk | 1.45.1 |
| opentelemetry-exporter-otlp-proto-common | 1.45.1 |

```
uv venv --python 3.12 .venv-semantic-kernel
uv pip install --python .venv-semantic-kernel/bin/python \
    semantic-kernel==1.45.0 \
    opentelemetry-sdk==1.45.1 opentelemetry-exporter-otlp-proto-common==1.45.1
OPENAI_API_KEY=... .venv-semantic-kernel/bin/python scripts/fixtures/semantic_kernel/capture.py \
    > tests/fixtures/semantic_kernel/invoke_prompt.json
```

Semantic Kernel's own telemetry is the only instrumentation; there is no
Traceloop or OpenInference package for it. The script turns on
SEMANTICKERNEL_EXPERIMENTAL_GENAI_ENABLE_OTEL_DIAGNOSTICS before importing
it. The sensitive variant of that flag sends message content through Python
logging, not span events, so it is left off and the file has no events.
