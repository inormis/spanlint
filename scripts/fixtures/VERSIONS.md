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
