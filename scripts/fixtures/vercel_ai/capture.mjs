// Runs one chat completion through the AI SDK under one of its two
// OpenTelemetry integrations and exports the spans over OTLP/HTTP to
// scripts/fixtures/otlp_receiver.py listening on port 4318. Needs
// OPENAI_API_KEY. Usage: node capture.mjs semconv|legacy

import { openai } from "@ai-sdk/openai";
import { LegacyOpenTelemetry, OpenTelemetry } from "@ai-sdk/otel";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-proto";
import { resourceFromAttributes } from "@opentelemetry/resources";
import { NodeTracerProvider, SimpleSpanProcessor } from "@opentelemetry/sdk-trace-node";
import { generateText, registerTelemetry } from "ai";

const integrations = { semconv: OpenTelemetry, legacy: LegacyOpenTelemetry };
const Integration = integrations[process.argv[2]];
if (Integration === undefined) {
  console.error("usage: node capture.mjs semconv|legacy");
  process.exit(2);
}

const provider = new NodeTracerProvider({
  resource: resourceFromAttributes({ "service.name": "spanlint-fixtures" }),
  spanProcessors: [
    new SimpleSpanProcessor(
      new OTLPTraceExporter({ url: "http://127.0.0.1:4318/v1/traces" }),
    ),
  ],
});
provider.register();
registerTelemetry(new Integration());

try {
  await generateText({
    model: openai.chat("gpt-4o-mini"),
    prompt: "Say hi in one word.",
    temperature: 0,
    maxOutputTokens: 16,
  });
} finally {
  await provider.shutdown();
}
